using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using AindJustFramesSchemas;
using System.Collections.Generic;

[Combinator]
[Description("Returns a formatted ZeroMQ connection string based on the provided NetworkConfig object.")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class NetworkConfigToConnectionString
{
    private string protocol = "tcp";
    public string Protocol
    {
        get { return protocol; }
        set { protocol = value; }
    }

    private ActionType action = ActionType.Connect;
    public ActionType Action
    {
        get { return action; }
        set { action = value; }
    }


    public IObservable<string> Process(IObservable<NetworkConfig> source)
    {
        return source.Select(value =>
        {
            string address = value.Address;
            System.Net.IPAddress ip;
            if (!(System.Net.IPAddress.TryParse(address, out ip) && ip.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                && !string.Equals(address, "localhost", StringComparison.OrdinalIgnoreCase))
            {
                throw new FormatException(string.Format("Invalid address format: {0}. Must be IPv4 or 'localhost'.", address));
            }

            return string.Format("{0}{1}://{2}:{3}",
            actionPrefixCharacter[Action],
            Protocol,
            address,
            value.Port);
        });
    }


    public enum ActionType
    {
        Connect,
        Bind,
        None
    }

    private readonly Dictionary<ActionType, string> actionPrefixCharacter = new Dictionary<ActionType, string>
    {
        { ActionType.Connect, ">" },
        { ActionType.Bind, "@" },
        { ActionType.None, "" }
    };
}
