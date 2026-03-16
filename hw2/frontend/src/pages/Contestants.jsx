import { CommonList } from "../components/CommonList";

export function Contestants()
{
    return <CommonList name="Contestants" url="/contestants" fields={["id", "name", "school"]} />
}
