using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using NetMQ;
using AindJustFramesSchemas.MessageProtocol;

[Combinator]
[Description("Tries to parse NetMQFrame as RegisteredMessages and filters out invalid messages")]
[WorkflowElementCategory(ElementCategory.Combinator)]
public class TryParseRegisteredMessages
{
    public IObservable<RegisteredMessages> Process(IObservable<NetMQFrame> source)
    {
        return source
            .Select(frame => frame.ConvertToString())
            .Select(messageString =>
            {
                try
                {
                    return Newtonsoft.Json.JsonConvert.DeserializeObject<RegisteredMessages>(messageString);
                }
                catch
                {
                    Console.WriteLine("Failed to parse message: " + messageString);
                    return null;
                }
            })
            .Where(msg => msg != null);
    }
}
