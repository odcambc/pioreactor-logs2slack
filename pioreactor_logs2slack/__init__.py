# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging

import click
from pioreactor.background_jobs.base import BackgroundJobContrib
from pioreactor.cli.pio import JOBS_TO_SKIP_KILLING
from pioreactor.config import config
from pioreactor.mureq import post
from pioreactor.types import MQTTMessage
from pioreactor.whoami import get_unit_name
from pioreactor.whoami import UNIVERSAL_EXPERIMENT


# since this is a long-running job, we don't want it to be killed by pio kill --all-jobs.
JOBS_TO_SKIP_KILLING.append("logs2slack")


class Logs2Slack(BackgroundJobContrib):
    job_name = "logs2slack"

    def __init__(self, unit: str, experiment: str) -> None:
        super(Logs2Slack, self).__init__(
            unit=unit, experiment=experiment, plugin_name="pioreactor_logs2slack"
        )
        self.slack_webhook_url = config.get("logs2slack", "slack_webhook_url")
        if not self.slack_webhook_url:
            self.logger.error("[logs2slack] slack_webhook_url is not defined in your config.ini.")
            raise ValueError("[logs2slack] slack_webhook_url is not defined in your config.ini.")

        self.log_level = config.get("logs2slack", "log_level", fallback="INFO")
        self.start_passive_listeners()

    def publish_to_slack(self, msg: MQTTMessage) -> None:
        payload = json.loads(msg.payload)

        # check to see if we should allow the logs based on the level.
        if getattr(logging, self.log_level) > getattr(logging, payload["level"]):
            return
        elif payload["task"] == self.job_name:
            # avoid an infinite loop, https://github.com/Pioreactor/pioreactor-logs2slack/issues/2
            return

        slack_msg = f"[{payload['level']}] [{self.unit}] [{payload['task']}] {payload['message']}"
        encoded_json = json.dumps({"text": slack_msg}).encode("utf-8")

        r = post(
            self.slack_webhook_url, body=encoded_json, headers={"Content-Type": "application/json"}
        )

        r.raise_for_status()

    def start_passive_listeners(self) -> None:
        self.subscribe_and_callback(self.publish_to_slack, f"pioreactor/{self.unit}/+/logs/+")


@click.command(name="logs2slack")
def click_logs2slack() -> None:
    """
    turn on logging to Slack
    """

    lg = Logs2Slack(unit=get_unit_name(), experiment=UNIVERSAL_EXPERIMENT)
    lg.block_until_disconnected()
