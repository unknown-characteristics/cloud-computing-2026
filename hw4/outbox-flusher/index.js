const { DefaultAzureCredential } = require('@azure/identity');

module.exports = async function (context, myTimer) {
    // 1. Define your endpoint/audience pairs
    const tasks = [
        { 
            url: 'https://user-service.blackocean-b29efe40.polandcentral.azurecontainerapps.io', 
            scope: 'api://caeaf18f-428a-4621-abe9-2d953fb3e116/.default' 
        },
        { 
            url: 'https://submissions-service.blackocean-b29efe40.polandcentral.azurecontainerapps.io', 
            scope: 'api://c8e29bf0-7c23-4798-8532-a1ccbbe05c47/.default' 
        },
        { 
            url: 'https://assignments-service.blackocean-b29efe40.polandcentral.azurecontainerapps.io', 
            scope: 'api://a96435c9-fb5d-4e46-a8d1-783dc58eaa13/.default' 
        }
    ];

    const credential = new DefaultAzureCredential();

    if (myTimer.isPastDue) {
        context.log('Timer trigger is running late.');
    }

    // 2. Map tasks to a list of Promises
    const requests = tasks.map(async (task) => {
        try {
            // Fetch a unique token for THIS specific audience
            const tokenResponse = await credential.getToken(task.scope);
            const token = tokenResponse.token;

            const response = await fetch(task.url + "/outbox/pending-events", {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ triggeredBy: 'AzureFunction', timestamp: new Date().toISOString() })
            });

            context.log(`Success: [${task.url}] - Status: ${response.status}`);
        } catch (err) {
            context.log.error(`Failed: [${task.url}] - Error: ${err.message}`);
        }
    });

    // 3. Fire all requests in parallel and wait for them to finish
    await Promise.allSettled(requests);
    
    context.log('Finished processing all scheduled tasks.');
};
