import { useNavigate } from "react-router-dom";
import { api } from '../api/api';
import { useState, useEffect } from "react";
import qs from "qs"
import { Alert, Box, Button, Container, Paper, TextField, Typography } from "@mui/material";
import { useAuth } from '../context/AuthContext';
import { getAPIErrorMessage } from "../utils/response";

export function Login()
{
    const { user, login } = useAuth();

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    useEffect(() => {
        if(user) return navigate("/");
    }, [user]);

    async function submitLogin(e)
    {
        e.preventDefault();
        setError("");

        try
        {
            const data = qs.stringify({username, password});

            const res = await api.post("/users/login", data, {
                headers: {"Content-Type": "application/x-www-form-urlencoded"}
            });

            login(res.data.access_token);
        } 
        catch(err)
        {
            console.error(err);
            console.log(err.response);
            setError(`Could not login: ${getAPIErrorMessage(err.response)}`);
        }
    }

    return (
        <Container>
            <Paper sx={{padding: 4}}>
                <Typography variant="h4" gutterBottom textAlign="center">
                    Login
                </Typography>
                {error && (
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error}
                    </Alert>
                )}

                <Box component="form" onSubmit={submitLogin} sx={{display: "flex", flexDirection: "column", gap: 2}}>
                    <TextField label="Username" variant="outlined" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                    <TextField label="Password" variant="outlined" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                    <Button type="submit" variant="contained" color="primary">
                        Login
                    </Button>
                </Box>
            </Paper>
        </Container>
    )
}
