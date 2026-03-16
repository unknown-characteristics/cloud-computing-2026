import { useCallback, useState } from "react"
import { api } from "../api/api"
import { useNavigate, useParams } from "react-router-dom"
import { getAPIErrorMessage } from "../utils/response"
import { Alert, Button, Paper, TextField, Typography } from "@mui/material"

export function CreatePrize()
{
    const {contest_id} = useParams();

    const [description, setDescription] = useState("")
    const [estimatedValue, setEstimatedValue] = useState(0)
    const [initialQuantity, setInitialQuantity] = useState(0)

    const [error, setError] = useState();

    const navigate = useNavigate();

    const submitPrize = useCallback((description, estimatedValue, initialQuantity) => {
        const request = {description, estimated_value: estimatedValue, initial_qty: initialQuantity}
        api.post(`/contests/${contest_id}/prizes`, request).then(response => {
            navigate(`/contests/${contest_id}/prizes/${response.data.prize_id}`);
        }).catch(err => {
            setError(getAPIErrorMessage(err.response));
        });
    }, [navigate, contest_id])
    return (
        <Paper sx={{padding: 2, display: "flex", flexDirection: "column", gap: 1}}>
            <Typography variant="h4" gutterBottom>Create Prize</Typography>
            {error && <Alert severity="error" sx={{marginBottom: 1}}>{error}</Alert>}

            <TextField label="description" value={description} onChange={e => setDescription(e.target.value)}></TextField>
            <TextField label="estimated value" type="number" value={estimatedValue} onChange={e => setEstimatedValue(e.target.value)}></TextField>
            <TextField label="initial quantity" type="number" value={initialQuantity} onChange={e => setInitialQuantity(e.target.value)}></TextField>

            <Button variant="outlined" color="primary" onClick={() => submitPrize(description, estimatedValue, initialQuantity)}>Submit</Button>
        </Paper>
    )
}
