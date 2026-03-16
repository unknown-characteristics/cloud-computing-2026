import { useParams } from "react-router-dom";
import { ContestView } from "../components/ContestView";

export function ContestPage()
{
    const { id } = useParams();

    return <ContestView id={id} />;
}
