import importlib.util
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCREENS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "Python"
    / "Screens"
)
RENDERER_PATH = SCREENS / "CvIndustryFlowRenderer.py"
ADVISOR_PATH = SCREENS / "CvIndustryAdvisor.py"


def load_renderer():
    extensions = types.ModuleType("CvPythonExtensions")

    class WidgetTypes:
        WIDGET_GENERAL = 0

    extensions.WidgetTypes = WidgetTypes
    extensions.CyGlobalContext = lambda: object()
    extensions.CyArtFileMgr = lambda: object()
    sys.modules["CvPythonExtensions"] = extensions
    sys.modules["CvUtil"] = types.ModuleType("CvUtil")

    spec = importlib.util.spec_from_file_location(
        "industry_flow_renderer_test_module", RENDERER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordingScreen:
    def __init__(self):
        self.pieces = []

    def addDDSGFCAt(
        self,
        widget_id,
        parent_id,
        path,
        x,
        y,
        width,
        height,
        widget_type,
        data1,
        data2,
        option,
    ):
        self.pieces.append(
            {
                "widget": widget_id,
                "path": path,
                "x": x,
                "y": y,
                "w": width,
                "h": height,
            }
        )


class IndustryFlowRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_renderer()

    def new_renderer(self):
        return self.module.CvIndustryFlowRenderer(lambda name: name)

    def piece(self, screen, suffix):
        for piece in screen.pieces:
            if piece["widget"].endswith(suffix):
                return piece
        self.fail("Missing rendered piece ending in %s" % suffix)

    def test_downward_corner_path_is_continuous(self):
        renderer = self.new_renderer()
        screen = RecordingScreen()
        renderer._drawCornerPath(
            screen,
            "scroll",
            "Edge",
            "line_x",
            "line_y",
            "corner_xy",
            "corner_xmy",
            "corner_mxmy",
            "corner_mxy",
            "head",
            100,
            100,
            200,
            300,
            180,
        )

        first_corner = self.piece(screen, "EdgeBCorner")
        vertical = self.piece(screen, "EdgeCLine")
        second_corner = self.piece(screen, "EdgeDCorner")
        final_line = self.piece(screen, "EdgeELine")

        self.assertEqual(first_corner["x"], 200)
        self.assertEqual(vertical["x"], 200)
        self.assertEqual(second_corner["x"], 200)
        self.assertEqual(vertical["y"], 108)
        self.assertEqual(vertical["h"], 72)
        self.assertEqual(final_line["x"], 208)

    def test_upward_corner_path_is_continuous(self):
        renderer = self.new_renderer()
        screen = RecordingScreen()
        renderer._drawCornerPath(
            screen,
            "scroll",
            "Edge",
            "line_x",
            "line_y",
            "corner_xy",
            "corner_xmy",
            "corner_mxmy",
            "corner_mxy",
            "head",
            100,
            180,
            200,
            300,
            100,
        )

        first_corner = self.piece(screen, "EdgeBCorner")
        vertical = self.piece(screen, "EdgeCLine")
        second_corner = self.piece(screen, "EdgeDCorner")

        self.assertEqual(first_corner["x"], vertical["x"])
        self.assertEqual(vertical["x"], second_corner["x"])
        self.assertEqual(vertical["y"], 108)
        self.assertEqual(vertical["h"], 72)

    def test_edge_types_receive_separate_aligned_lanes(self):
        renderer = self.new_renderer()
        positions = {
            "from": {"x": 0, "y": 0, "w": 100, "h": 94},
            "to": {"x": 400, "y": 160, "w": 220, "h": 108},
        }
        edges = [
            {"from": "from", "to": "to", "type": "flow"},
            {"from": "from", "to": "to", "type": "corp_founding"},
            {"from": "from", "to": "to", "type": "corp_input"},
        ]

        routes = renderer._buildEdgeRoutes(positions, edges)
        lanes = [route["laneX"] for route in routes]

        self.assertEqual(len(set(lanes)), 3)
        for route in routes:
            self.assertEqual(route["laneX"] % renderer.LINE_THICKNESS, 0)
            self.assertGreaterEqual(
                route["laneX"], route["startX"] + renderer.LINE_THICKNESS * 2
            )
            self.assertLessEqual(
                route["laneX"], route["endX"] - renderer.LINE_THICKNESS * 3
            )
        self.assertLess(routes[0]["laneX"], routes[1]["laneX"])
        self.assertLess(routes[1]["laneX"], routes[2]["laneX"])

    def test_overlapping_vertical_spans_do_not_reuse_lane(self):
        renderer = self.new_renderer()
        usage = {}
        first = renderer._chooseLaneX("flow", 100, 20, 300, 180, usage)
        second = renderer._chooseLaneX("flow", 100, 40, 300, 160, usage)
        third = renderer._chooseLaneX("flow", 100, 220, 300, 300, usage)

        self.assertNotEqual(first, second)
        self.assertEqual(first, third)


class IndustryAdvisorFilterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ADVISOR_PATH.read_text(encoding="utf-8")

    def test_filter_controls_use_all_declared_flow_filters(self):
        self.assertIn(
            "for kFilter in CvIndustryFlowData.getFlowFilters():", self.source
        )
        self.assertIn("IndustryChainsFilter_%s", self.source)
        self.assertIn("self.flowFilterWidgetIds[szWidgetId] = szFilterId", self.source)

    def test_filter_selection_persists_and_is_clickable(self):
        controls = self.source.split("def _drawChainsControls", 1)[1].split(
            "def _drawChainsLegend", 1
        )[0]
        self.assertNotIn(
            "self.szFlowFilter = CvIndustryFlowData.FILTER_ALL", controls
        )
        self.assertIn("if self.flowFilterWidgetIds.has_key(fname):", self.source)
        self.assertIn(
            "self.szFlowFilter = self.flowFilterWidgetIds[fname]", self.source
        )

    def test_default_view_is_a_readable_single_family(self):
        self.assertIn("self.szFlowFilter = 'corp1'", self.source)


if __name__ == "__main__":
    unittest.main()
