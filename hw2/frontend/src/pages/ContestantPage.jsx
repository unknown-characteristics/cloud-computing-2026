import { useParams } from "react-router-dom";
import { ContestantProfile } from "../components/ContestantProfile";

export function ContestantPage()
{
    const { id } = useParams();

    return <ContestantProfile id={id} />;
}
