import { Navigate, useNavigate } from "react-router-dom";
import { api } from '../api/api';
import { useState } from "react";
import qs from "qs"
import { Alert, Box, Button, Container, Paper, TextField, Typography } from "@mui/material";
import { useAuth } from '../context/AuthContext';
import { getAPIErrorMessage } from "../utils/response";

export function Register()
{
    const { user, login } = useAuth();

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [name, setName] = useState("");
    const [school, setSchool] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    if(user) return navigate("/");

    async function submitRegister(e)
    {
        e.preventDefault();
        setError("");

        try
        {
            const data = {username, password, name, email, school};

            const res = await api.post("/users/register", data);

            navigate("/");
        } 
        catch(err)
        {
            console.error(err);
            setError(`Could not register: ${getAPIErrorMessage(err.response)}`);
        }
    }

    return (
        <Container>
            <Paper sx={{padding: 4}}>
                <Typography variant="h4" gutterBottom textAlign="center">
                    Register
                </Typography>
                {error && (
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error}
                    </Alert>
                )}

                <Box component="form" onSubmit={submitRegister} sx={{display: "flex", flexDirection: "column", gap: 2}}>
                    <TextField label="Username" variant="outlined" value={username} onChange={(e) => setUsername(e.target.value)} required/>
                    <TextField label="Email" type="email" variant="outlined" value={email} onChange={(e) => setEmail(e.target.value)} required/>
                    <TextField label="Name" variant="outlined" value={name} onChange={(e) => setName(e.target.value)} required/>
                    <TextField label="School" variant="outlined" value={school} onChange={(e) => setSchool(e.target.value)} required/>
                    <TextField label="Password" variant="outlined" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                    <Button type="submit" variant="contained" color="primary">
                        Register
                    </Button>
                </Box>
            </Paper>
        </Container>
    )
}
