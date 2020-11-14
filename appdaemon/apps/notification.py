"""Define automations for notifications."""
from typing import Union, Callable

from appbase import AppBase


class Notifications(AppBase):
    """Define a class for Notification handling."""

    # pylint: disable=too-many-instance-attributes

    class Notification:
        """Define a notification object."""

        def __init__(self, channel, message, targets, title=None, **kwargs):
            """Initialize."""
            self.channel = channel
            self.message = message
            self.title = title
            self.targets = targets
            self.repeat = kwargs.get("repeat")
            self.interval = kwargs.get("interval")
            self.data = kwargs.get("data")
            if self.data is None:
                self.data = {}
            self.cancel = None

    def configure(self) -> None:
        """Configure."""
        self.briefing = []
        persons = self.adbase.get_state("person")
        for person in persons:
            # Listen for person arriving at home
            self.adbase.listen_state(
                self.send_briefing,
                person,
                attribute="non_binary_presence",
                new="just_arrived",
            )
            # Listen for person waking up
            self.adbase.listen_state(
                self.send_briefing, person, attribute="sleep_state", new="awake"
            )

    def send_briefing(
        self, entity: Union[str, dict], attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        """Send all notifications in the briefing list."""
        for notification in self.briefing:
            notification.cancel(delete=True)
            self.send_notification(notification)

    def notify(
        self,
        channel: str,
        message: str,
        targets: Union[str, list],
        title: str = None,
        repeat: bool = False,
        interval: Union[int, None] = None,
        data: Union[dict, None] = None,
    ) -> Callable:
        """Return an object to send a notification."""
        return self.send_notification(
            self.Notification(
                channel,
                message,
                targets=targets,
                title=title,
                repeat=repeat,
                interval=interval,
                data=data,
            )
        )

    def send_notification(self, notification: Notification) -> Callable:
        """Send single or repeating notification and
           return a method to cancel notification"""
        if not notification.repeat:
            handle = self.adbase.run_in(self.send, 0, notification=notification)
        else:
            handle = self.adbase.run_every(
                self.send, "now", notification.interval, notification=notification
            )

        def cancel(delete: bool = False) -> None:
            """Define a method to cancel the notification."""
            self.adbase.cancel_timer(handle)
            if delete:
                self.briefing.remove(notification)

        notification.cancel = cancel
        self.briefing.append(notification)

        return cancel

    def send(self, kwargs: dict) -> None:
        """Send a notification."""
        notification = kwargs["notification"]
        targets = self.get_targets(notification.targets, notification.channel)
        targets_flat = [target for notifiers in targets for target in notifiers]

        for target in targets_flat:
            self.hass.call_service(
                f"notify/{target}",
                title=notification.title,
                message=notification.message,
                data=notification.data,
            )
            self.adbase.log(
                f"Nachricht: "
                f"{notification.title if notification.title else notification.message}"
                f" an {target}"
            )

        if targets and not notification.repeat and notification in self.briefing:
            self.briefing.remove(notification)

        if not targets and notification.repeat:
            notification.cancel()

    def get_targets(self, targets: Union[str, list], channel: str) -> Union[str, list]:
        """Return available targets."""
        if channel == "emergency":
            return [
                self.adbase.get_state(f"person.{target}", attribute="notifiers")
                for target in targets
            ]
        return [
            self.adbase.get_state(f"person.{target}", attribute="notifiers")
            for target in targets
            if self.target_available(target)
        ]

    def target_available(self, target: str) -> bool:
        """Return True if target is available."""
        sleep_state = self.adbase.get_state(f"person.{target}", attribute="sleep_state")
        # Remove after full implementation of bed sensors
        sleep_state = "awake"
        home = self.adbase.get_state(f"person.{target}", attribute="home")
        return home and sleep_state == "awake"
