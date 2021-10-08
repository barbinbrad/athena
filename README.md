# Athena

Athena is a JSON RPC proxy server that accepts a websocket connection from an edge device and allows clients to send RPC requests to the edge device by making traditional HTTP requests to the proxy server. 


## Getting Started

To get started, clone the repo, and install the dependencies.

```
git clone https://github.com/barbinbrad/athena
pip install -r requirements.txt
cd athena
```

To start the proxy server run:

```
python3 server.py
```

You'll notice that a proxy server is not very interesting on it own. 

To connect an edge device, open a new terminal tab, and go to the `examples` folder:

```
cd examples
python3 device-12345.py
```

Still not much. You may have noticed that the server terminal picked up a websocket connection (or two).

Finally we add a client. This could be an app, another API, or anything really. In our example, we'll stick to python.

Open another terminal, navigate to the `examples` folder and run:

```
python3 client-12345.py
```

You should see that requests from the client are sent to the proxy over HTTP, and then forwarded to the device over websocket. And finally the result it returned to client over HTTP.

Now let's make things more interesting. 

Try opening up more terminals running the same `client-12345.py` file. This creates many race conditions. But the server should return the correct results to the correct requester.

This is accomplished by setting the `id` property of the JSON RPC request, and using a `PriorityQueue` to return results.

## JSON RPC

A valid JSON RPC request looks this:

```json
{
    "method": "nameOfTheFunctionToCall",
    "id": 0,
    "params": {
        "these": "are",
        "totally": "optional"
    },
    "jsonrpc": "2.0"   
}
```

The request needs a `method`, `id`, and `jsonrpc`. The params are optional. They are passed as arguments to the `@dispatch.add_method` function.

Check out the examples for a better understanding of this.