from __future__ import annotations


class FakeRect:
    left = 1
    top = 2
    right = 101
    bottom = 202


class FakeControl:
    def __init__(self, *, text: str, class_name: str, control_type: str = ""):
        self._text = text
        self._class_name = class_name
        self.element_info = type("Info", (), {"control_type": control_type, "class_name": class_name})()

    def window_text(self):
        return self._text

    def class_name(self):
        return self._class_name

    def rectangle(self):
        return FakeRect()


class FakeWindow:
    def descendants(self):
        return [
            FakeControl(text="one", class_name="QWidget", control_type="Pane"),
            FakeControl(text="two", class_name="QWidget", control_type="Pane"),
            FakeControl(text="three", class_name="QWidget", control_type="Pane"),
        ]


def test_parashara_light_control_payload_keeps_text_class_type_and_rect():
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _control_payload

    payload = _control_payload(FakeControl(text="Haridas", class_name="QWidget", control_type="Pane"), index=3)

    assert payload == {
        "index": 3,
        "text": "Haridas",
        "class_name": "QWidget",
        "control_type": "Pane",
        "rect": {"left": 1, "top": 2, "right": 101, "bottom": 202},
    }


def test_parashara_light_class_summary_counts_control_types_and_classes():
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _class_summary

    summary = _class_summary(
        [
            {"control_type": "Pane", "class_name": "QWidget"},
            {"control_type": "Pane", "class_name": "QWidget"},
            {"control_type": "Button", "class_name": ""},
        ]
    )

    assert summary == [
        {"control_type": "Pane", "class_name": "QWidget", "count": 2},
        {"control_type": "Button", "class_name": "", "count": 1},
    ]


def test_parashara_light_screenshot_failure_is_recorded(tmp_path):
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _attach_screenshot

    payload = {}
    _attach_screenshot(
        payload,
        object(),
        tmp_path / "pl.png",
        image_factory=lambda window: (_ for _ in ()).throw(RuntimeError("PIL missing")),
    )

    assert payload["screenshot_error"] == "PIL missing"


def test_parashara_light_screenshot_success_records_path_and_closes_image(tmp_path):
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _attach_screenshot

    class FakeImage:
        def __init__(self):
            self.saved_to = None
            self.closed = False

        def save(self, target):
            self.saved_to = target

        def close(self):
            self.closed = True

        def getextrema(self):
            return ((0, 255), (0, 255), (0, 255))

    image = FakeImage()
    target = tmp_path / "pl.png"
    payload = {}

    _attach_screenshot(payload, object(), target, image_factory=lambda window: image)

    assert payload["screenshot"] == str(target)
    assert payload["screenshot_blank"] is False
    assert image.saved_to == target
    assert image.closed is True


def test_parashara_light_screenshot_records_blank_image(tmp_path):
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _attach_screenshot

    class BlankImage:
        def save(self, target):
            pass

        def close(self):
            pass

        def getextrema(self):
            return ((0, 0), (0, 0), (0, 0))

    payload = {}
    _attach_screenshot(payload, object(), tmp_path / "blank.png", image_factory=lambda window: BlankImage())

    assert payload["screenshot_blank"] is True


def test_parashara_light_capture_controls_respects_limit():
    from apps.calculations.management.commands.capture_parashara_light_ui_state import _capture_controls

    controls = _capture_controls(FakeWindow(), max_controls=2)

    assert [control["text"] for control in controls] == ["one", "two"]


def test_build_parashara_light_witness_batch_packets_includes_artifact_plan(tmp_path):
    from apps.calculations.management.commands.build_parashara_light_witness_batch_packets import (
        build_parashara_light_witness_batch_packets,
    )

    output_root = tmp_path / "pl7" / "batch-queue"

    payload = build_parashara_light_witness_batch_packets(
        output_root=output_root,
        case_ids=["sterlitamak-1998-04-30-1345"],
        force=True,
    )

    row = payload["created"][0]

    assert row["paths"]["packet"].endswith("packet.json")
    assert row["paths"]["manual_values_template"].endswith("manual-values-template.json")
    assert row["artifact_plan"]["parashara_light"]["packet_dir"] == str(
        output_root / "sterlitamak-1998-04-30-1345"
    )
    assert any(
        check["name"] == "manual_values_template" and check["exists"] is True
        for check in row["artifact_plan"]["parashara_light"]["checks"]
    )
    index = (output_root / "_index.json").read_text(encoding="utf-8")
    assert "artifact_plan" in index
