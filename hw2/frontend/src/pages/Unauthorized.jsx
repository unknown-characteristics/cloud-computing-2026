import { Container, Typography, Paper } from "@mui/material";

export function Unauthorized()
{
    return (
        <Container sx={{marginTop: 4}}>
            <Paper sx={{padding: 3}}>
                <Typography variant="h5" color="error">
                    Access denied
                </Typography>
            </Paper>
        </Container>
    )
}
