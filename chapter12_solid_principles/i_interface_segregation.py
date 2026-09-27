"""
Chapter 12 — Interface Segregation Principle.
Don't force a class to implement methods it doesn't need.
"""
from abc import ABC, abstractmethod


def section(title):
    print(f"\n{'=' * 10} {title} {'=' * 10}")


# ---------------------------------------------------------------------------
section("BAD: one bloated interface forces irrelevant methods")
# ---------------------------------------------------------------------------
class NotifierInterfaceBad(ABC):
    """Every notifier is forced to implement ALL of these, even if a
    given channel genuinely can't support some of them."""
    @abstractmethod
    def send_text(self, message: str) -> None: ...
    @abstractmethod
    def send_image(self, image_path: str) -> None: ...
    @abstractmethod
    def send_video(self, video_path: str) -> None: ...

class SmsNotifierBad(NotifierInterfaceBad):
    def send_text(self, message: str) -> None:
        print(f"  [SMS] {message}")
    def send_image(self, image_path: str) -> None:
        raise NotImplementedError("SMS cannot send images")   # forced, meaningless method
    def send_video(self, video_path: str) -> None:
        raise NotImplementedError("SMS cannot send video")    # forced, meaningless method

sms = SmsNotifierBad()
sms.send_text("Your order shipped")
try:
    sms.send_image("photo.jpg")
except NotImplementedError as e:
    print(f"  Forced to implement, then forced to fail loudly: {e}")

print("\nProblem: SmsNotifierBad MUST provide send_image/send_video just to")
print("satisfy the interface, even though neither makes sense for SMS.")


# ---------------------------------------------------------------------------
section("GOOD: small, focused interfaces -- implement only what applies")
# ---------------------------------------------------------------------------
class SupportsText(ABC):
    @abstractmethod
    def send_text(self, message: str) -> None: ...

class SupportsImage(ABC):
    @abstractmethod
    def send_image(self, image_path: str) -> None: ...

class SupportsVideo(ABC):
    @abstractmethod
    def send_video(self, video_path: str) -> None: ...

class SmsNotifierGood(SupportsText):
    """Only implements what SMS genuinely supports -- nothing forced."""
    def send_text(self, message: str) -> None:
        print(f"  [SMS] {message}")

class WhatsAppNotifierGood(SupportsText, SupportsImage, SupportsVideo):
    """Implements more, because it genuinely CAN support more."""
    def send_text(self, message: str) -> None:
        print(f"  [WhatsApp] {message}")
    def send_image(self, image_path: str) -> None:
        print(f"  [WhatsApp] sending image: {image_path}")
    def send_video(self, video_path: str) -> None:
        print(f"  [WhatsApp] sending video: {video_path}")

def notify_text_only(notifier: SupportsText, message: str) -> None:
    notifier.send_text(message)   # works with EITHER notifier below

notify_text_only(SmsNotifierGood(), "Your order shipped")
notify_text_only(WhatsAppNotifierGood(), "Your order shipped")

print("\nSmsNotifierGood never has to implement send_image/send_video at all --")
print("it simply doesn't claim to support SupportsImage/SupportsVideo.")


# ---------------------------------------------------------------------------
section("When NOT to over-apply this")
# ---------------------------------------------------------------------------
print("If every real implementation genuinely supports every method anyway,")
print("splitting one interface into five tiny ones just adds navigation")
print("overhead with no actual flexibility gained. ISP earns its cost when")
print("implementations GENUINELY vary in what they can support.")
