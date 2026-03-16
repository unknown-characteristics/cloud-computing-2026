import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect } from "react";
import { Alert, Box, Button, Container, Dialog, Paper, Typography } from "@mui/material";
import { api } from "../api/api";
import { CommonEditor } from "./CommonEditor";
import { getAPIErrorMessage } from "../utils/response";

export function UserProfile({ id, dataOverride })
{
    const { user, role, logout } = useAuth();
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState("");

    const [modalOpen, setModalOpen] = useState(false);

    useEffect(() => {
        setUserData(null);
        setError("");
        api.get(`/users/${id}`).then(response => {
            setUserData(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [id]);

    useEffect(() => {
        if(dataOverride)
            setUserData(dataOverride);
    }, [dataOverride])

    async function handleEdit(data, errorCallback)
    {
        const request = {};
        if(data["username"] != "" && data["username"] != userData.username)
            request["username"] = data["username"];
        if(data["password"] != "")
            request["password"] = data["password"];
        if(data["email"] != "" && data["email"] != userData.email)
            request["email"] = data["email"];
        if(data["role"] != "" && data["role"] != userData.role)
            request["role"] = data["role"];

        if(Object.keys(request).length == 0)
        {
            setModalOpen(false);
            return;
        }

        try
        {
            const response = await api.patch(`/users/${id}`, request);
            
            setUserData(response.data);
            setModalOpen(false);
        }
        catch(err)
        {
            errorCallback(getAPIErrorMessage(err.response));
        }
    }

    async function deleteUser()
    {
        setError("");
        try
        {
            const response = await api.delete(`/users/${id}`);

            if(userData.id == user.sub)
                logout();
            setUserData(null);
        }
        catch(error)
        {
            setError(`Cannot delete profile: ${getAPIErrorMessage(error.response)}`);
        }
    }

    return (
        <Container>
            <Paper sx={{padding: 2}}>
                <Typography variant="h4" gutterBottom>
                    User profile
                </Typography>

                {(!userData || error) && <Box>
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error ? error : "Missing user"}
                    </Alert>
                </Box>}

                {userData && <Box>
                <Typography variant="h6">User ID</Typography>
                <Typography>{userData.id}</Typography>
                <Typography variant="h6">Contestant ID</Typography>
                <Typography>{userData.contestant_id}</Typography>
                <Typography variant="h6">Username</Typography>
                <Typography>{userData.username}</Typography>
                <Typography variant="h6">Email</Typography>
                <Typography>{userData.email}</Typography>
                <Typography variant="h6">Role</Typography>
                <Typography>{userData.role}</Typography>

                {(role === "admin" || user.sub == id) && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => setModalOpen(true)}>
                        Edit profile
                    </Button>
                    <Button color="inherit" variant="outlined" onClick={() => deleteUser()}>
                        Delete user
                    </Button>
                    <Button color="inherit" variant="outlined" component={Link} to={`/contestants/${userData.contestant_id}`}>
                        View contestant
                    </Button>
                    <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
                        <CommonEditor name="profile" fields={{"username": "text", "password": "password", "email": "email", "role": "text"}} defaults={{"username": userData.username, "email": userData.email, "role": userData.role}} callback={handleEdit} />
                    </Dialog>
                </Box>}
                
                </Box>}
            </Paper>
        </Container>
    )
}
