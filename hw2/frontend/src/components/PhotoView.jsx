import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export function PhotoView({photoData})
{
    return (
        <Box>
            <Box component="img" src={photoData.photo_url} alt="Prize Photo" sx={{objectFit: "contain", width: "100%", height: "100%"}} />
            <Box>
                <Link to={photoData.photo_page_url} target="_blank" rel="noopener noreferrer" underline="hover">Photo</Link>
                <Typography sx={{display: "inline"}}> by </Typography>
                <Link to={photoData.author_url} target="_blank" rel="noopener noreferrer" underline="hover">{photoData.author_name}</Link>
                <Typography sx={{display: "inline"}}> on </Typography>
                <Link to="https://unsplash.com/" target="_blank" rel="noopener noreferrer" underline="hover">Unsplash</Link>
            </Box>
        </Box>
    )
}