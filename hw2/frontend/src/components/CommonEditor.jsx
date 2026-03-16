import { Alert, Button, Paper, TextField, Typography } from "@mui/material";
import { useCallback, useEffect, useState } from "react";

export function CommonEditor({name, fields, defaults, callback})
{
    const [data, setData] = useState();
    const [error, setError] = useState();

    useEffect(() => {
        const dataObject = {}
        for(const key in fields)
        {
            if(defaults && key in defaults)
                dataObject[key] = defaults[key];
            else
                dataObject[key] = "";
        }

        setData(dataObject);
    }, []);

    const updateData = useCallback((key, value) => {
        setData(prevData => ({...prevData, [key]: value}));
    }, [setData]);

    const errorCallback = useCallback((msg) => {
        setError(`Failed to modify data: ${msg}`);
    }, [setError])

    return (
        <Paper sx={{padding: 2, display: "flex", flexDirection: "column"}}>
            <Typography variant="h4" gutterBottom>Edit {name}</Typography>
            {error && <Alert severity="error" sx={{marginBottom: 2}}>{error}</Alert>}
            {data && Object.keys(fields).map((val, idx) =>
                [
                    // <Typography key={`${val}_title`} variant="h6">{val}</Typography>,
                    <TextField key={`${val}_field`} sx={{marginBottom: 1}} type={fields[val]} label={val} value={data[val] || ""} onChange={e => updateData(val, e.target.value)}></TextField>
                ]
            )}
            <Button variant="contained" sx={{marginTop: 1}} onClick={() => callback(data, errorCallback)}>Save changes</Button>
        </Paper>
    )
}
