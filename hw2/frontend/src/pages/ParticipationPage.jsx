import { useParams } from "react-router-dom";
import { ParticipationView } from "../components/ParticipationView";

export function ParticipationPage()
{
    const { contest_id, contestant_id } = useParams();

    return <ParticipationView contest_id={contest_id} contestant_id={contestant_id} />;
}
