export function getAPIErrorMessage(response)
{
    if(!response || !response.data)
        return "Internal Server Error"

    if(response.data == "")
    {
        if(response.status == 404)
            return "Not found";
        else
            return "Unknown error";
    }

    if(response.data == "Internal Server Error")
        return "Internal Server Error";

    if(response.data.detail !== undefined)
    {
        if(typeof response.data.detail === "string")
            return response.data.detail;
        else
            return response.data.detail[0].msg;
    }

    if(response.data.msg !== undefined)
        return response.data.msg;

    return "Unknown error";
}
