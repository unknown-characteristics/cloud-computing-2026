import { useCallback, useState } from "react"
import { api } from "../api/api"
import { useNavigate } from "react-router-dom"
import { getAPIErrorMessage } from "../utils/response"
import { Alert, Button, Paper, TextField, Typography } from "@mui/material"

export function CreateContest()
{
    const [name, setName] = useState("")
    const [difficulty, setDifficulty] = useState(0)
    const [solution, setSolution] = useState("")
    const [hint, setHint] = useState("")
    const [status, setStatus] = useState("active")

    const [error, setError] = useState();

    const navigate = useNavigate();

    const submitContest = useCallback((name, difficulty, solution, hint, status) => {
        const request = {name, difficulty, solution, hint, status}
        api.post("/contests", request).then(response => {
            navigate(`/contests/${response.data.id}`);
        }).catch(err => {
            setError(getAPIErrorMessage(err.response));
        });
    }, [navigate])
    return (
        <Paper sx={{padding: 2, display: "flex", flexDirection: "column", gap: 1}}>
            <Typography variant="h4" gutterBottom>Create contest</Typography>
            {error && <Alert severity="error" sx={{marginBottom: 1}}>{error}</Alert>}

            <TextField label="name" value={name} onChange={e => setName(e.target.value)}></TextField>
            <TextField label="difficulty" type="number" value={difficulty} onChange={e => setDifficulty(e.target.value)}></TextField>
            <TextField label="solution" value={solution} onChange={e => setSolution(e.target.value)}></TextField>
            <TextField label="hint" value={hint} onChange={e => setHint(e.target.value)}></TextField>
            <TextField label="status" value={status} onChange={e => setStatus(e.target.value)}></TextField>

            <Button variant="outlined" color="primary" onClick={() => submitContest(name, difficulty, solution, hint, status)}>Submit</Button>
        </Paper>
    )
}
