using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Linq;
using System.Reactive.Linq;
using AindJustFramesSchemas.MessageProtocol;
using System.Reactive;

[Combinator]
[Description("")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class BuildRegisteredMessage
{
    private MessageType messageType = MessageType.Event;
    public MessageType MessageType
    {
        get { return messageType; }
        set { messageType = value; }
    }

    private const int protocolVersion = 0;

    private string rigName;
    public string RigName
    {
        get { return rigName; }
        set { rigName = value; }
    }

    public IObservable<RegisteredMessages> Process(IObservable<RegisteredPayload> source)
    {
        return Process(source.Select(value => new Timestamped<RegisteredPayload>(value, DateTimeOffset.UtcNow)));
    }

    public IObservable<RegisteredMessages> Process(IObservable<Timestamped<RegisteredPayload>> source)
    {
        string hostname = Environment.MachineName;
        string processId = System.Diagnostics.Process.GetCurrentProcess().Id.ToString();
        return source.Select(value => new RegisteredMessages()
        {
            MessageType = MessageType,
            ProtocolVersion = protocolVersion,
            Timestamp = value.Timestamp,
            ProcessId = processId,
            Hostname = hostname,
            RigName = RigName,
            Payload = value.Value
        });
    }
}
