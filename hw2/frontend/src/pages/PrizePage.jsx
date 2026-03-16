import { useParams } from "react-router-dom";
import { PrizeView } from "../components/PrizeView";

export function PrizePage()
{
    const { contest_id, prize_id } = useParams();

    return <PrizeView contest_id={contest_id} prize_id={prize_id} />;
}
