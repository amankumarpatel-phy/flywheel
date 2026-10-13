# Flywheel Lab Simulator

An interactive Streamlit teaching workstation for the undergraduate flywheel experiment. It includes an automatically rotating flywheel animation, a falling-mass experiment mode, live physics calculations, observation trials, and interactive plots.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Open Streamlit Community Cloud and connect your GitHub account.
2. Select this repository.
3. Set the main file path to `app.py`.
4. Deploy.

## Features

- Automatic flywheel rotation demo with speed control.
- Falling-mass experiment with acceleration, string detachment, and frictional deceleration.
- Moment of inertia calculation using the standard energy method.
- Trial table, CSV download, and angular-velocity graph.
- Theory, assumptions, and viva questions.

## Model assumptions

The post-detachment stage assumes approximately constant angular deceleration. The standard energy method also assumes the frictional work per revolution is approximately the same during both stages. Simulation values are illustrative and should not be reported as actual laboratory measurements.
