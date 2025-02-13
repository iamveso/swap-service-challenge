# INSTALLATION PROCESS

1. To install ensure you have python3 installed on your device
2. create a virtual environment (preferrable but not necessary) using the command [python -m venv .<venv>] where name is what you want to name your virtual environment
3. run the command [ pip3 install -r requirements.txt ]. This will install all dependencied of the project
4. Make sure you have redis installed on your device too
5. to start the server, after installing dependencies, run the command [ uvicorn main:app ]
6. Go to localhost:8000/graphql to view the graphql endpoints and localhost:8000/graph/image to see a visual representation of the graph constructed from the data

# ARCHITECTURE

Overall the project has a very simple architecture. The core functionality is placed in an "app" with each file handling a specific aspect of the overall solution. Then there is the main.py file that lives outside the app folder together with other files listed out in this section

# main.py

Handles initialization and running the application. Background processes, fastapi init and strawberry are all handled here. it is important for this file ot remain small and easily readable

# settings.py

Any application setting is put here. usually this would also handle reading variables from an .env file should one be needed

# models.py

All fastapi models are declared in this file. Currently this only includes Token and Pool. as the application grows larger more models will need to be stored and the possibility of breaking the file into smaller files under the models folder should be considered

# schema.py

Similar to models.py but for the decalring models relating to the graphql endpoint. Graphql queries and mutations are also handled in this file. Like models.py as the project grows larger and more endpoints are added breaking up the file to smaller files under the schema folder will be more appropriate

# utils.py

Handles functions that may be needed across the app to handle basic utilities but is not specific to the core solution of the app itself. an example is string manipulation to parse the token names

# pool_loader.py

This is one of the most important parts of the project. The project relies heavily on the accuracy of information stored by this file. THis handles calling and parsing the information returned from coingecko's endpoint.

# path_finder.py

Another very crucial piece of the app is located in this file. Here the algorithm for storing the information received from pool_loader in a graph and finding the best swap path is written. It also handles updating the graph with new pool data as this needs to be a frequent routine

Other parts of the folder include

# static

Stores the png file displayed on the rest endpoint to view the graph

# requirements.txt

a text file that lists all the dependencies of the project

# SOME TECHNICAL DECISIONS

# why use fastapi instead of django or flask

The simple answer is fastapi boast of being the fastest python framework. But also, it is seamless to work with async using fastapi and using pydantic a lot of validations are handled making it easier to focus on the solution itself

# tokens

The Token data structure stores the names of all the coins in a particular pool as a set. Ideally it would be nice to store the ID's also but that will require a dict and dicts cannot be used as set values. This is further complicated by the fact that some times similar swap transactions with little to no difference are repeated in the response. e.g USDT / WETH appearing twice and _MAY_ have different id's which would cause problems when generating the graph.

# networkx

Networkx is a popular python library for handling graph related problems. Writing everything from scratch is also viable but it takes time and may not be as efficient as battle tested solutions like networkx. Networkx also comes with enough flexibility that allows swapping algorithms should the need arise

# data structures

One of the trickiest part of the project was determing the optimal way to store information. There are only two things we need; Tokens and Pools. A token is essentially the name of a crypto coin. A pool holds two tokens, their price relative to each other (which is approximately the inverse of themselves) and the fee for carrying out the swap (should there be one).
Tokens are stored in a set list which is returned by the available_tokens endpoint in graphql
Pools are the main structure which is used to create the nodes, edges and weight ov the graph
The algorithm used for constructing the weights is written in the code [path_finder.py]

Also the response from the find_route endpoint returns the best path as a list of tokens and the overall rate. The list may have multiple tokens starting with the "from" token and ending with the "to" token. Tokens inbetween are intermediary coins that may need to be swapped to get the optimal price for reaching the "to" token. The rate is how many "to" tokens you can get from swapping 1 "from" token using this path.

# swap algorithm

The problem after being stored in the required data strcutrue is essentially a shortest path problem. There are a lot of ways to solve this issue but dijkstra's algorithm is sufficient. There is the possibility of using bellman-ford because of negative weights but I ultimately decided against that since negative weights are not expected and if they do appear then it can be exploited for infinite swap potential which can be an issue

# caching

An easy way to simulate caching is using in memory information. whenever the application is run, the pools and graph information can be stored as class fields which will make them live as long as the program works. There are a few issues with this, first being that as the number of requests increase, the app get slower and uses more memory. The second being that it joins storage with path finding. Also updating the information can become complex in large scales since while updating we should not read from the same memory. finally there are faster and more efficient methods which allow very fast reads of stored information while also making updating the information easy. redis is a popular choice. On extrememly large scales there _might_ be a need to also use a traditional database but considering we need are not storing any long term data this is unlikely.

The caching strategy used here is to simply cache the pool data returned from the endpoint. when we call the available_tokens or find_route endpoints we just fetch this information from the cache. This eliminates (unless at the start of the program) the need to call the endpoint manually and this will be handled by the background process

# updates
Using apscheduler, there's a backround process that runs every two minutes. The time was chosen arbitrarily. Using the api response, I will recommend using a scheduler of not more than 5 minutes since the api itself tracks changes to price every 5 mins.

# consideraions

1. for caching there are more sophisticated ways to handle this however this is a simple and efficient way that makes sure the response and graph are in sync (since the graph is computed from the pool list). This improves the performance enough and even at scale one of the largest bottlenecks is always external api calls.

2. If there are any deviations in the expectations of the api then that data is ignored. eg when getting the tokens name instead of USDT / WETH we may get USDT / WETH / USDC which does not conform to the quote and base token structure. a better approach will be to find which is actually the base token and the quote token but that will complicate the project a lot more.

3. Using async to run the shortest path computation also helps free computer resources to do other things while the computation is going on instead of blocking the main thread. However since the computation is a function in an async function, I would go for a more optimal algorithm such as A\* instead.

4. Cache best route results so we just read from the cache instead of running the computation again. To make sure we are not giving stale data, the cache is flushed whenever we get new data from the api
