import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect } from "react";
import { Alert, Box, Button, Container, Dialog, Paper, Typography } from "@mui/material";
import { api } from "../api/api";
import { CommonEditor } from "./CommonEditor";
import { getAPIErrorMessage } from "../utils/response";
import { CommonList } from "./CommonList";

export function ContestantProfile({ id, dataOverride })
{
    const { user, role, logout } = useAuth();
    const [contestantData, setContestantData] = useState(null);
    const [error, setError] = useState("");

    const [modalOpen, setModalOpen] = useState(false);

    useEffect(() => {
        setContestantData(null);
        setError("");
        api.get(`/contestants/${id}`).then(response => {
            setContestantData(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [id]);

    useEffect(() => {
        if(dataOverride)
            setContestantData(dataOverride);
    }, [dataOverride])

    async function handleEdit(data, errorCallback)
    {
        const request = {};
        if(data["name"] != "" && data["name"] != contestantData.name)
            request["name"] = data["name"];
        if(data["school"] != "" && data["school"] != contestantData.school)
            request["school"] = data["school"];
    
        if(Object.keys(request).length == 0)
        {
            setModalOpen(false);
            return;
        }

            
        try
        {
            const response = await api.patch(`/contestants/${id}`, request);
            
            setContestantData(response.data);
            setModalOpen(false);
        }
        catch(err)
        {
            errorCallback(getAPIErrorMessage(err.response));
        }
    }

    return (
        <Container sx={{display: "flex", gap: 3, flexDirection: "column"}}>
            <Paper sx={{padding: 2}}>
                <Typography variant="h4" gutterBottom>
                    Contestant profile
                </Typography>

                {(!contestantData || error) && <Box>
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error ? error : "Missing contestant"}
                    </Alert>
                </Box>}

                {contestantData && <Box>
                <Typography variant="h6">Contestant ID</Typography>
                <Typography>{contestantData.id}</Typography>
                <Typography variant="h6">Name</Typography>
                <Typography>{contestantData.name}</Typography>
                <Typography variant="h6">School</Typography>
                <Typography>{contestantData.school}</Typography>

                {(role === "admin" || user.contestant_id == id) && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => setModalOpen(true)}>
                        Edit contestant
                    </Button>
                    <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
                        <CommonEditor name="profile" fields={{"name": "text", "school": "text"}} defaults={{"name": contestantData.name, "school": contestantData.school}} callback={handleEdit} />
                    </Dialog>
                </Box>}

                </Box>}
            </Paper>
            
                {(role === "admin" || user.contestant_id == id) && <CommonList name="Participations" fields={["contest_id"]} id_key="contest_id" url={`/contestants/${id}/participations`} />}
        </Container>
    )
}
