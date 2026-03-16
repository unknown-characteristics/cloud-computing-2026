import { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"
import { jwtDecode } from "jwt-decode"
import { isTokenExpired } from "../utils/token";

const AuthContext = createContext();

export function AuthProvider({children}) {
    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    const [user, setUser] = useState(token ? jwtDecode(token) : null);

    function login(token) {
        localStorage.setItem("token", token);
        setUser(jwtDecode(token));
        navigate("/");
    }

    function logout()
    {
        localStorage.removeItem("token");
        setUser(null);
        navigate("/");
    }

    const role = user?.role;

    useEffect(() => {
        if(!user) return;

        if(isTokenExpired(user))
            logout();
    }, [user]);

    return (
        <AuthContext.Provider value= {{user, role, login, logout}}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth()
{
    return useContext(AuthContext);
}
