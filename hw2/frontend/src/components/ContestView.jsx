import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect, useCallback } from "react";
import { Alert, Box, Button, Container, Dialog, Paper, Typography } from "@mui/material";
import { api } from "../api/api";
import { CommonEditor } from "./CommonEditor";
import { getAPIErrorMessage } from "../utils/response";
import { CommonList } from "./CommonList";
import { ParticipationView } from "./ParticipationView";

export function ContestView({ id, dataOverride })
{
    const { user, role } = useAuth();
    const [contestData, setContestData] = useState(null);
    const [error, setError] = useState("");
    const [partData, setPartData] = useState(null);

    const [modalOpen, setModalOpen] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        if(!user || user.role == "admin") return;

        setPartData(null);
        api.get(`/contests/${id}/participations/${user.contestant_id}`).then(response => {
            setPartData(response.data);
        }).catch (err => {
            setPartData(null);
        })
    }, [id, user]);


    useEffect(() => {
        setContestData(null);
        setError("");
        api.get(`/contests/${id}`).then(response => {
            setContestData(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [id]);

    useEffect(() => {
        if(dataOverride)
            setContestData(dataOverride);
    }, [dataOverride])

    async function handleEdit(data, errorCallback)
    {
        const request = {};
        if(data["name"] != "" && data["name"] != contestData.name)
            request["name"] = data["name"];
        if(data["solution"] != "" && data["solution"] != contestData.solution)
            request["solution"] = data["solution"];
        if(data["difficulty"] != "" && data["difficulty"] != contestData.difficulty)
            request["difficulty"] = data["difficulty"];

        request["hint"] = data["hint"];

        if(data["status"] != "" && data["status"] != contestData.status)
            request["status"] = data["status"];

        if(Object.keys(request).length == 0)
        {
            setModalOpen(false);
            return;
        }
   
        try
        {
            const response = await api.patch(`/contests/${id}`, request);
            
            setContestData(response.data);
            setModalOpen(false);
        }
        catch(err)
        {
            errorCallback(getAPIErrorMessage(err.response));
        }
    }

    const deleteContest = useCallback(() => {
        api.delete(`/contests/${id}`).then(response => {
            setContestData(null);
        }).catch(err => {
            setError(getAPIErrorMessage(err.response))
        })
    })

    const enrollContest = useCallback(() => {
        api.post(`/contests/${id}/participations`, {contestant_id: user.contestant_id, contest_id: id}).then(response => {
            setPartData(response.data);
        }).catch(err =>
            setError(`Couldn't enroll: ${getAPIErrorMessage(err.response)}`)
        )
    }, [id, user])

    const createPrize = useCallback(() => {
        navigate(`/contests/${id}/prizes/create`);
    }, [id, navigate])

    return (
        <Container sx={{display: "flex", gap: 3, flexDirection: "column"}}>
            <Paper sx={{padding: 2}}>
                <Typography variant="h4" gutterBottom>
                    Contest data
                </Typography>

                {(!contestData || error) && <Box>
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error ? error : "Missing contest"}
                    </Alert>
                </Box>}

                {contestData && <Box>
                <Typography variant="h6">Contest ID</Typography>
                <Typography>{contestData.id}</Typography>
                <Typography variant="h6">Name</Typography>
                <Typography>{contestData.name}</Typography>
                <Typography variant="h6">Hint</Typography>
                <Typography>{contestData.hint || "(None)"}</Typography>
                <Typography variant="h6">Difficulty</Typography>
                <Typography>{contestData.difficulty}</Typography>
                <Typography variant="h6">Status</Typography>
                <Typography>{contestData.status}</Typography>
                <Typography variant="h6">Start time</Typography>
                <Typography>{contestData.start_time}</Typography>
                <Typography variant="h6">End time</Typography>
                <Typography>{contestData.end_time || "Ongoing"}</Typography>
                {role === "admin" && [
                    <Typography key={1} variant="h6">Solution</Typography>,
                    <Typography key={2}>{contestData.solution}</Typography>
                ]}


                {role === "admin" && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => setModalOpen(true)}>
                        Edit contest
                    </Button>
                    <Button color="inherit" variant="outlined" onClick={() => deleteContest()}>
                        Delete contest
                    </Button>
                    <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
                        <CommonEditor name="profile" fields={{"name": "text", "solution": "text", "hint": "text", "status": "text", "difficulty": "number"}} defaults={{"name": contestData.name, "hint": contestData.hint, "difficulty": contestData.difficulty, "status": contestData.status, "solution": contestData.solution}} callback={handleEdit} />
                    </Dialog>
                </Box>}

                {role === "contestant" && !partData && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => enrollContest()}>Enroll</Button>
                </Box>}

                </Box>}
            </Paper>
    
            {role === "admin" && <CommonList name="Participations" fields={["contestant_id"]} id_key="contestant_id" url={`/contests/${id}/participations`} />}
            {role === "contestant" && partData && 
            <ParticipationView contest_id={id} contestant_id={user.contestant_id} dataOverride={partData}></ParticipationView>}

            {contestData?.status === "ended" && <CommonList name="Leaderboard" fields={["contestant_id", "score", "award_id"]} view={false} url={`/contests/${id}/leaderboard`}></CommonList>}
            <CommonList name="Prizes" fields={["prize_id", "description", "estimated_value"]} url={`/contests/${id}/prizes`} id_key="prize_id" createCallback={role === "admin" && contestData?.status === "active" ? createPrize : null}></CommonList>
        </Container>
    )
}
