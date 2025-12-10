# Aind.Behavior.JustFrames

A repository with code for a online video acquisition/encoding pipeline

## ZeroMQ Architecture

![ZeroMQ Architecture](assets/zmq_architecture.svg)

## Notes on workflow startup

Button -> EnableExperiment
EnableExperiment(unit) -> StartLogging(unit) -> StartExperiment (unit)
                       -> StartLogging -> IsExperimentRunning(bool)

In main:
zmqRequest (master) -> EnableExperiment

In satellite:
zmqRequest (satellite) -> EnableExperiment

## Refactored

In master:

Button | zmqRequest -> TryStart ( _ = >{
zmqRequest (satellite) -> EnableExperiment(satellite) -> HasStarted .zip(). timeout}
) -> EnableExperiment -> StartLogging -> StartExperiment -> Trigger