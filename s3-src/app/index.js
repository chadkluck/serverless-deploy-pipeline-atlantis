console.log ("COLD START");

// we'll bring in tools. Tools also has the AWS functions (tools.AWS)
var tools = require("./tools.js");

/* can't go directly to CONFIG as we need to wait for the promise in the handler 
(we can't 'await' out here since we are not in an async function, however node.js 14
will allow for await at the root level) */
const CONFIG_PROMISE = tools.appInit(
	{
		params: [
			{ // You can have multiple sets, each with their own path
				"path": process.env.paramStorePath, // use either env variable or hard code the parameter path (eg. "/WebApp/lds/myapp/myparameter")
				"names": [ 
					"sharedSecret", 
					// add additional paramers for this path
				]
			}, 
			// add additional paths with their parameters
		],
		settings: {
			answers: [ 
				"It is certain",
				"It is decidedly so",
				"Without a doubt",
				"Yes definitely",
				"You may rely on it",
				"As I see it, yes",
				"Most likely",
				"Outlook good",
				"Yes",
				"Signs point to yes",
				"Reply hazy try again",
				"Ask again later",
				"Better not tell you now",
				"Cannot predict now",
				"Concentrate and ask again",
				"Don't count on it",
				"My reply is no",
				"My sources say no",
				"Outlook not so good"
			],
		}
	}
);

/* variables to keep application state such as temporary tokens or counters 
that can be stored and used while the Lambda instance is kept in a warm state. 
The values are shared among requests and should only store application state, 
not request state */
var appState = {};

/**
 * This is the get function for your application referred to in the SAM 
 * template. It should be kept simple and used as the handler for the 
 * request. Business logic should be put in processRequest()
 * 
 * @param {*} event 
 * @param {*} context 
 * @param {*} callback 
 * @returns 
 */
exports.get = async (event, context, callback) => {

    try {
        /* wait for CONFIG to be settled as we need it before continuing. This is set up as
        Promise.all so it may be extended in the future to allow for additional promises
        to be kept */
        const [ CONFIG ] = await Promise.all([CONFIG_PROMISE]); // additional promises to wait for can be added
        const response = await processRequest(event, context, CONFIG); // process the request and wait for the result
        callback(null, response); // send the result back to Gateway API
    } catch (error) {
        return { // return an error message
            statusCode: 500,
            body: JSON.stringify({
                message: 'Internal server error in 7G' // 7G just so we know it is an app and not API Gateway error
            })
        };
    };
};

/**
 * Process the request
 * 
 * @param {array} event The event passed to the lambda function
 * @param {array} context The context passed to the lambda function
 * @param {array} CONFIG the Cache-Proxy app config comprising of Environment and Paramstore variables
 * @returns {array} Response to send up to AWS API Gateway
 */
const processRequest = async function(event, context, CONFIG) {

	/* Variables used in the request */
	var reqVars = {};

	var response = null;
	var data = null;

	// do something
	var rand = Math.floor(Math.random() * CONFIG.settings.answers.length);

	var prediction = CONFIG.settings.answers[rand];

	// Gets sent to CloudWatch logs. Check it out!
	console.log(`Prediction log: ${prediction}`);

	// place the prediction inside of a data object to return back to client
	var data = {
		item: prediction
	};

	response = {
		statusCode: 200,
		body: JSON.stringify(data),
		headers: {'content-type': 'application/json'}
	}; 

	return response;
}