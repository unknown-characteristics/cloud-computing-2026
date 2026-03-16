import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect } from "react";
import { Alert, Box, Button, Container, Dialog, Paper, Typography } from "@mui/material";
import { api } from "../api/api";
import { CommonEditor } from "./CommonEditor";
import { getAPIErrorMessage } from "../utils/response";

export function ParticipationView({ contest_id, contestant_id, dataOverride })
{
    const { user, role } = useAuth();
    const [partData, setPartData] = useState(null);
    const [error, setError] = useState("");

    const [modalOpen, setModalOpen] = useState(false);

    useEffect(() => {
        setPartData(null);
        setError("");

        if(dataOverride)
            return;
        api.get(`/contests/${contest_id}/participations/${contestant_id}`).then(response => {
            setPartData(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [contest_id, contestant_id, dataOverride]);

    useEffect(() => {
        if(dataOverride)
            setPartData(dataOverride);
    }, [dataOverride])

    async function handleEdit(data, errorCallback)
    {
        const request = {};
        if(data["answer"] != "" && data["answer"] != partData.answer)
            request["answer"] = data["answer"];
        if(data["score"] != "" && data["score"] != partData.score)
            request["score"] = data["score"];

        if(Object.keys(request).length == 0)
        {
            setModalOpen(false);
            return;
        }

        try
        {
            const response = await api.patch(`/contests/${contest_id}/participations/${contestant_id}`, request);
            
            setPartData(response.data);
            setModalOpen(false);
        }
        catch(err)
        {
            errorCallback(getAPIErrorMessage(err.response));
        }
    }

    async function deleteParticipation()
    {
        setError("");
        try
        {
            const response = await api.delete(`/contests/${contest_id}/participations/${contestant_id}`);
            setPartData(null);
        }
        catch(error)
        {
            setError(`Cannot delete participation: ${getAPIErrorMessage(error.response)}`);
        }
    }

    return (
        <Container>
            <Paper sx={{padding: 2}}>
                <Typography variant="h4" gutterBottom>
                    Contestant submission
                </Typography>

                {(!partData || error) && <Box>
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error ? error : "Missing participation"}
                    </Alert>
                </Box>}

                {partData && <Box>
                <Typography variant="h6">Contest ID</Typography>
                <Typography>{partData.contest_id}</Typography>
                <Typography variant="h6">Contestant ID</Typography>
                <Typography>{partData.contestant_id}</Typography>
                <Typography variant="h6">Answer</Typography>
                <Typography>{partData.answer || "(None)"}</Typography>
                <Typography variant="h6">Score</Typography>
                <Typography>{partData.score}</Typography>

                {(role === "admin" || user.contestant_id == contestant_id) && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => setModalOpen(true)}>
                        Edit participation
                    </Button>
                    <Button color="inherit" variant="outlined" onClick={() => deleteParticipation()}>
                        Delete participation
                    </Button>
                    <Button color="inherit" variant="outlined" component={Link} to={`/contestants/${partData.contestant_id}`}>
                        View contestant
                    </Button>
                    <Button color="inherit" variant="outlined" component={Link} to={`/contests/${partData.contest_id}`}>
                        View contest
                    </Button>
                    <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
                        {role === "admin" && <CommonEditor name="participation" fields={{"answer": "text", "score": "text"}} defaults={{"answer": partData.answer, "score": partData.score}} callback={handleEdit} />}
                        {role === "contestant" && <CommonEditor name="participation" fields={{"answer": "text"}} defaults={{"answer": partData.answer}} callback={handleEdit} />}
                    </Dialog>
                </Box>}
                
                </Box>}
            </Paper>
        </Container>
    )
}
