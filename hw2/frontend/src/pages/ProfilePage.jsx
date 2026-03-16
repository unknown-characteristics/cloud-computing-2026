import { useParams } from "react-router-dom";
import { UserProfile } from "../components/UserProfile";

export function ProfilePage()
{
    const { id } = useParams();

    return <UserProfile id={id} />;
}
