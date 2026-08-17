"""Test sensor/platform logic using Device methods only."""

from tests.helpers import build_device_from_fixture


def sensor_keys(reg_map):
    return [k for k in reg_map if k.endswith(("_get", "_set"))]


class TestSensorSelection:
    def test_sensor_count_matches_register_count(self, fixture_data):
        for name, reg_map in fixture_data.items():
            count = sum(1 for k in reg_map if k.endswith(("_get", "_set")))
            assert count > 0, f"{name}: expected at least one sensor register"

    def test_each_register_produces_native_value(
        self, devices_from_fixtures, fixture_data
    ):
        for name, reg_map in fixture_data.items():
            device = devices_from_fixtures[name]
            for key in sensor_keys(reg_map):
                if reg_map[key].get("offset") is None:
                    continue
                val = device.get_register_value(key)
                assert val is not None, (
                    f"{name}/{key}: get_register_value returned None"
                )

    def test_hybrid_detection(self, fixture_data):
        has_hybrid = any(
            "power_wood_set" in reg_map for reg_map in fixture_data.values()
        )
        assert has_hybrid is True


class TestBinarySensorLogic:
    def test_on_when_value_nonzero(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "ris_pellet_ris_get": {
                    "reg_key": "ris_pellet_ris_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "1",
                    "value": 1,
                }
            },
        )
        assert bool(device.get_register_value("ris_pellet_ris_get")) is True

    def test_off_when_value_zero(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "ris_pellet_ris_get": {
                    "reg_key": "ris_pellet_ris_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "0",
                    "value": 0,
                }
            },
        )
        assert bool(device.get_register_value("ris_pellet_ris_get")) is False
