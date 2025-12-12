using Bonsai;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Linq;
using System.Reactive.Linq;
using AindJustFramesSchemas.MessageProtocol;

[Combinator]
[Description("Ensures that all responses correspond to the payload type specified in the original broadcast request.")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class VerifyBroadcastResponse
{
    private bool throwOnMismatch = true;
    public bool ThrowOnMismatch
    {
        get { return throwOnMismatch; }
        set { throwOnMismatch = value; }
    }
    
    public IObservable<bool> Process(IObservable<Tuple<IList<RegisteredMessages>, RegisteredPayload>> source)
    {
        return Process(source.Select(tuple => Tuple.Create(tuple.Item2, tuple.Item1)));
    }

    public IObservable<bool> Process(IObservable<Tuple<RegisteredPayload, IList<RegisteredMessages>>> source)
    {
        return source.Select(value =>
        {
            var request = value.Item1;
            var responses = value.Item2;
            var expectedPayloadType = request.GetType().Name;
            foreach(var response in responses)
            {
                var responsePayloadType = response.Payload.GetType().Name;
                if (responsePayloadType != expectedPayloadType)
                {
                    if (ThrowOnMismatch){
                        throw new InvalidOperationException(string.Format("Response payload type '{0}' does not match the expected payload type '{1}'. Response={2}", responsePayloadType, expectedPayloadType, response));
                    }
                    else
                    {
                        return false;
                    }
                }
            }
            return true;
        });
    }
}
