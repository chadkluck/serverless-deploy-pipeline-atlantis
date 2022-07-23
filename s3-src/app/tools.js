// tools.js

/**
 * 
 */

// AWS functions
var AWS = require("aws-sdk");
AWS.config.update({region: process.env.AWS_REGION});

/**
 * Performs loading of config from various resources in an async fashion to 
 * limit load time during Cold Starts.
 * 
 * Right now it supports:
 * - SSM Parameter Store
 * - Setting of settings variables
 * 
 * It could be expanded to support:
 * - JSON config files from S3
 * - DynamoDb
 * - Establishing DB connections
 * - Settings set by functions (async evaluate each settings object to see if it is a function then execute that function)
 * 
 * An annonymous object containing paths and resources is passed in and a promise for
 * a config object is passed back.
 * 
 * Usage:
 * 
    const CONFIG_PROMISE = appInit(
		{
			params: [
				{ // You can have multiple sets, each with their own path
					"path": process.env.paramStorePath, // use either env variable or hard code the parameter path (eg. "/WebApp/lds/myapp/myparameter")
					"names": [ 
						"example_param1", 
						"example_param2",
						// add additional paramers for this path
					]
				}, 
				// add additional paths with their parameters
			],
			settings: {
				myVar1: true,
				myVar2: Math.random(), // perform calculations
				myVar3: (process.env.detailedLogs === 1 && process.env.deployEnvironment === "PROD"), // logically set values
				// add additional setting variables
			}
		}
	);

 *	In the example above it would return an object to CONFIG_PROMISE:

	{
        params: {}, // object with key-value pairs
        settings: {} // object with key-value pairs
    }

 *  In your code you can set CONFIG once all the promises are returned:
 *  const [ CONFIG ] = await Promise.all([CONFIG_PROMISE]); // additional promises to wait for can be added
 *
 * @param {Object} init containing parameter paths and names and settings
 * @returns {Object} with resolved parameter values and settings
 */
const appInit = async (init) => {

    /**
     * Retreive all the parameters (listed in const params) from the
     * parameter store and parse out the name. Then return the name
     * along with their value.
     * 
     * This will automatically decrypt any encrypted values (it will
     * leave any String and StringList parameters as their normal,
     * unencrypted self (WithDecryption is ignored for them))
     * 
     * @returns {array} parameters and their values
     */
    const getParametersFromStore = async function () {

        var ssm = new AWS.SSM();
        var paramstore = {};

        /* go through PARAMS and compile all parameters with 
        their paths pre-pended into a list of names */
        var paramNames = function () {
            let names = [];

            /* we have two levels to work through, the base path has param names 
            grouped under it. So get all the names within each base path grouping. */
            init.params.forEach(function(item) {
                item.names.forEach(function(p) {
                    names.push(item.path+p);
                });
            });
            return names;
        };

        /* put the list of full path names into query.Names */
        const query = {
            'Names': paramNames(),
            'WithDecryption': true
        };
        
        // get parameters from query - wait for the promise to resolve
        var request = await ssm.getParameters(query).promise();

        /* now that the promise has resolved, crop off the path and store key
        and value. Note that if there are name collisions some will be
        overwritten. (/webapp/myvar1 will overwrite /appconfig/myvar1) */
        request.Parameters.forEach(param => {
            const nameSections = param.Name.split('/'); // get the last part of the name
            const name = nameSections[nameSections.length - 1];

            // store key and value
            paramstore[name] = param.Value;
        });

        // return an array of keys and values
        return paramstore;
    };

    /**
     * This is an intermediary wait.
     */
    const getParameters = async function () {
        var resp = await getParametersFromStore();
        return resp;
    };

    // make the call to get the parameters and wait before proceeding to the return
    const ssmParameters = await getParameters();
    
    // now that we have our parameters from the store, combine them with the settings we received into a single Object structure for CONFIG
    return {
        params: ssmParameters, // object with key-value pairs
        settings: init.settings // object with key-value pairs		    
	};

};

module.exports = {
    AWS,
    appInit
};