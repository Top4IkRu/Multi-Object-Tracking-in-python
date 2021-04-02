from dataclasses import asdict

import numpy as np
import pytest
from mot.common.state import State
from mot.configs import GroundTruthConfig, SensorModelConfig
from mot.measurement_models import (
    ConstantVelocityMeasurementModel,
    RangeBearingMeasurementModel,
)
from mot.motion_models import ConstantVelocityMotionModel, CoordinateTurnMotionModel
from mot.scenarios.scenario_configs import (
    linear_sot,
    nonlinear_sot,
)
from mot.simulator import MeasurementData
from mot.simulator.measurement_data_generator import MeasurementData
from mot.simulator.object_data_generator import ObjectData
from mot.single_object_trackers import NearestNeighbourTracker
from mot.utils import Plotter
from mot.utils.visualizer import Plotter
from mot.utils.get_path import get_images_dir


@pytest.mark.parametrize(
    "config, motion_model, meas_model, name, tracker_initial_state",
    [
        (
            linear_sot,
            ConstantVelocityMotionModel,
            ConstantVelocityMeasurementModel,
            "SOT linear case (CV)",
            State(x=np.array([-40, -40, 15.0, 5.0]), P=100.0 * np.eye(4)),
        ),
        (
            nonlinear_sot,
            CoordinateTurnMotionModel,
            RangeBearingMeasurementModel,
            "SOT non linear case (CT)",
            State(
                x=np.array([0, 0, 10, 0, np.pi / 180]),
                P=np.power(np.diag([1, 1, 1, 1 * np.pi / 180, 1 * np.pi / 180]), 2),
            ),
        ),
    ],
)
@pytest.mark.parametrize("tracker", [(NearestNeighbourTracker)])
def test_tracker(
    config, motion_model, meas_model, name, tracker, tracker_initial_state
):
    config = asdict(config)
    ground_truth = GroundTruthConfig(**config)
    motion_model = motion_model(**config)
    sensor_model = SensorModelConfig(**config)
    meas_model = meas_model(**config)

    object_data = ObjectData(
        ground_truth_config=ground_truth, motion_model=motion_model, if_noisy=False
    )
    meas_data = MeasurementData(
        object_data=object_data, sensor_model=sensor_model, meas_model=meas_model
    )

    # Single object tracker parameter setting
    P_G = 0.999  # gating size in percentage
    w_minw = 1e-3  # hypothesis pruning threshold
    merging_threshold = 2  # hypothesis merging threshold
    M = 100  # maximum number of hypotheses kept in MHT

    tracker = tracker(
        meas_model=meas_model,
        sensor_model=sensor_model,
        motion_model=motion_model,
        gating_size=P_G,
    )

    tracker_estimations = tracker.estimate(
        initial_state=tracker_initial_state, measurements=meas_data
    )

    Plotter.plot(
        [tracker_estimations, meas_data, object_data],
        out_path=get_images_dir(__file__) + "/" + name + ".png",
    )
