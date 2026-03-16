import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { AppBar, Toolbar, Button, Box, Typography } from "@mui/material";

function Navbar()
{
    const {role, logout, user} = useAuth();

    return (
        <AppBar position="static">
            <Toolbar>
                <Typography variant="h6" sx={{flexGrow: 1}}>
                    contREST
                </Typography>
            </Toolbar>

            <Box sx={{display: "flex", flexDirection: "row"}}>
                <Box>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    {role === "admin" && <Button color="inherit" component={Link} to="/users">Users</Button>}
                    {role === "admin" && <Button color="inherit" component={Link} to="/contestants">Contestants</Button>}
                    {user && <Button color="inherit" component={Link} to="/contests">Contests</Button>}
                </Box>
                <Box sx={{flex: 1}}></Box>
                <Box>
                    {!user && [
                        <Button key={"login"} color="inherit" component={Link} to="/login">Login</Button>,
                        <Button key={"register"} color="inherit" component={Link} to="/register">Register</Button>
                    ]}
                    {user && [
                        <Button key={"logout"} color="inherit" onClick={logout}>Logout</Button>,
                        <Button key={"profile"} color="inherit" component={Link} to={`/users/${user.sub}`}>Profile</Button>
                    ]}
                </Box>
          </Box>
        </AppBar>
    )
}

export default Navbar;