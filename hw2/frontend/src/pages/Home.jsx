import { Container, Paper, Typography } from "@mui/material";
import { useAuth } from "../context/AuthContext";

export function Home()
{
    const {role} = useAuth();

    return (
        <Container sx={{marginTop: 4}}>
            <Paper sx={{padding: 3, marginBottom: 2}}>
                <Typography variant="h4" gutterBottom>
                    Home
                </Typography>
                {role === "admin" && <Typography>Welcome, Admin!</Typography>}
                {role === "contestant" && <Typography>Welcome, Contestant!</Typography>}
                {!role && <Typography>Welcome!</Typography>}
            </Paper>
        </Container>
    )
}
