from pathlib import Path

from vtf.eval.adapters import MockModelAdapter


def test_mock_adapter_accepts_a_test_image(tmp_path: Path) -> None:
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"not-a-real-image-but-a-test-payload")
    adapter = MockModelAdapter(response="Answer: 42")

    assert adapter.ask(image_path, "What is the answer?") == "Answer: 42"
    assert adapter.calls == 1


def test_mock_adapter_can_return_a_sequence_for_integration_tests(tmp_path: Path) -> None:
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"image")
    adapter = MockModelAdapter(responses=["Answer: 1", "Answer: 2"])

    assert adapter.ask(image_path, "q1") == "Answer: 1"
    assert adapter.ask(image_path, "q2") == "Answer: 2"
    assert adapter.calls == 2
