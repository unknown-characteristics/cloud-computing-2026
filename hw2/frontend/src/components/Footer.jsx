import { Box, Typography } from "@mui/material";

export function Footer()
{
    return (
        <Box component="footer" sx={{marginTop: "auto"}}>
            <Typography variant="body1" color="textSecondary">
                Data provided by API Ninjas & Gemini API & Unsplash API
            </Typography>
        </Box>
    )
}