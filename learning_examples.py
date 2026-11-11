"""Explicitly mapped educational examples for sufficient scalar formula inputs."""

EXAMPLES = {
    "cylinder": ["geom-cylinder"],
    "frustum": ["geom-frustum"],
    "mass": ["geom-mass", "unit-volume"],
    "limits": ["tol-limits", "tol-target"],
    "external": ["stock-ext"],
    "stock-minimum": ["stock-min"],
    "curvature": ["stock-compact-curvature"],
    "allowance": ["stock-allowance"],
    "cut-length": ["bar-required"],
    "cut-stop": ["bar-stop"],
    "capacity": ["bar-capacity"],
    "bars": ["bar-single-length"],
    "rpm": ["go-spindle-1", "go-constant-n.spindle-1"],
    "speed": ["go-constant-n.speed-1"],
    "feed": ["go-feed-1", "go-constant-n.feed-1", "go-linear-feed.per-revolution-1"],
    "tooth-feed": ["go-linear-feed.per-tooth-1"],
    "travel": ["go-linear-feed.total-travel-1"],
    "motion-time": ["go-time-1", "go-axial-feed.time-1", "go-linear-feed.time-1"],
    "chip": ["go-chip-1"],
    "specific-force": ["go-specific-force-1"],
    "force": ["go-force-1", "go-boring.force-1"],
    "power": ["go-net-power-1", "go-boring.engaged-net-power-1"],
    "torque": ["go-torque-1"],
    "drive-power": ["go-drive-power-1", "go-boring.engaged-drive-power-1"],
    "turned-diameter": ["go-longitudinal.diameter-1"],
    "longitudinal-volume": ["go-longitudinal.volume-1"],
    "longitudinal-rate": ["go-longitudinal.rate-1"],
    "facing": ["go-facing.travel-1", "go-facing.volume-1", "go-facing.rate-1"],
    "boring": ["go-boring.depth-1", "go-boring.area-1", "go-boring.volume-1"],
    "drill-tip": ["go-drilling.tip-1", "go-drilling-cycle.final-depth-1"],
    "saw": [
        "go-bandsaw.area-1",
        "go-bandsaw.time-1",
        "go-bandsaw.volume-1",
        "go-bandsaw.rate-1",
    ],
    "thread": ["go-thread.feed-rate-1", "go-thread.feed-time-1"],
    "lead": ["go-tapping.lead-1"],
    "inclined-path": ["go-inclined.travel-1"],
    "grinding-stroke": ["go-grinding.stroke-1", "go-grinding.position-1"],
    "batch-time": ["time-batch"],
    "inspection": ["time-inspection-sample"],
    "labor": ["labor-coefficient"],
    "hour-cost": ["cost-hour"],
    "unit-cost": ["cost-unit"],
}

BY_ARTICLE = {
    article: kind for kind, articles in EXAMPLES.items() for article in articles
}

# A worked chain can support several articles, each with its own main result.
PRIMARY_RESULTS = {
    "unit-volume": [("cubicMeters", "V", "м³")],
    "tol-limits": [("lower", "x_min", "мм"), ("upper", "x_max", "мм")],
    "go-facing.travel-1": [("L", "L", "мм")],
    "go-facing.volume-1": [("V", "V", "мм³")],
    "go-boring.depth-1": [("a", "a", "мм")],
    "go-boring.area-1": [("A", "A", "мм²")],
    "go-drilling.tip-1": [("tip", "h_tip", "мм")],
    "go-bandsaw.area-1": [("A", "A", "мм²")],
    "go-bandsaw.volume-1": [("volume", "V_kerf", "мм³")],
    "go-bandsaw.rate-1": [("rate", "Q_kerf", "см³/мин")],
    "go-thread.feed-rate-1": [("feed", "u", "мм/мин")],
    "go-grinding.position-1": [
        ("low", "X_low", "мм"),
        ("high", "X_high", "мм"),
    ],
}
