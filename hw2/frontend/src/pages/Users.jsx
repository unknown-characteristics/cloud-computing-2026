import { CommonList } from "../components/CommonList";

export function Users()
{
    return <CommonList name="Users" url="/users" fields={["id", "username", "role"]} />
}
