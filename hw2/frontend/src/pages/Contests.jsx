import { useCallback } from "react";
import { CommonList } from "../components/CommonList";
import { useNavigate } from "react-router-dom";

export function Contests()
{
    const navigate = useNavigate();
    const createCallback = useCallback(() => {
        navigate("/contests/create");
    }, [navigate])
    return <CommonList name="Contests" url="/contests" fields={["id", "name", "status"]} createCallback={createCallback} />
}
