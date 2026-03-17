import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect, useCallback } from "react";
import { Alert, Box, Button, Container, Dialog, FormControl, FormControlLabel, Paper, Radio, RadioGroup, Typography } from "@mui/material";
import { api } from "../api/api";
import { CommonEditor } from "./CommonEditor";
import { getAPIErrorMessage } from "../utils/response";
import { PhotoView } from "./PhotoView";

export function PrizeView({ contest_id, prize_id, dataOverride })
{
    const { role } = useAuth();
    const [prizeData, setPrizeData] = useState(null);
    const [error, setError] = useState("");

    const [editOpen, setEditOpen] = useState(false);
    const [photoOpen, setPhotoOpen] = useState(false);

    const [photoChosen, setPhotoChosen] = useState(0);
    const [photoList, setPhotoList] = useState(null);

    useEffect(() => {
        setPrizeData(null);
        setError("");

        if(dataOverride)
            return;
        api.get(`/contests/${contest_id}/prizes/${prize_id}`).then(response => {
            setPrizeData(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [contest_id, prize_id, dataOverride]);
    
    useEffect(() => {
        if(!prizeData || role !== "admin" || photoOpen == false)
            return;

        setPhotoList(null);
        setError("");

        api.get(`/search-prize-photos`, {params: {description: prizeData.description}}).then(response => {
            setPhotoList(response.data);
        }).catch (err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [prizeData, photoOpen]);

    useEffect(() => {
        if(dataOverride)
            setPrizeData(dataOverride);
    }, [dataOverride])

    async function handleEdit(data, errorCallback)
    {
        const request = {};
        if(data["initial_qty"] != "" && data["initial_qty"] != prizeData.initial_qty)
            request["initial_qty"] = data["initial_qty"];
        if(data["description"] != "" && data["description"] != prizeData.description)
            request["description"] = data["description"];
        if(data["estimated_valued"] != "" && data["estimated_valued"] != prizeData.estimated_valued)
            request["estimated_valued"] = data["estimated_valued"];

        if(Object.keys(request).length == 0)
        {
            setEditOpen(false);
            return;
        }

        try
        {
            const response = await api.patch(`/contests/${contest_id}/prizes/${prize_id}`, request);
            
            setPrizeData(response.data);
            setEditOpen(false);
        }
        catch(err)
        {
            errorCallback(getAPIErrorMessage(err.response));
        }
    }

    async function deletePrize()
    {
        setError("");
        try
        {
            const response = await api.delete(`/contests/${contest_id}/prizes/${prize_id}`);
            setPrizeData(null);
        }
        catch(error)
        {
            setError(`Cannot delete prize: ${getAPIErrorMessage(error.response)}`);
        }
    }

    const handlePhotoChange = useCallback((e) => {
        e.preventDefault();

        api.patch(`/contests/${contest_id}/prizes/${prize_id}`, {photo_data: photoList[photoChosen]}).then(response => {
            setPrizeData(response.data);
            setPhotoOpen(false);
        }).catch(err => {
            setError(getAPIErrorMessage(err.response))
        })
    }, [photoList, photoChosen, contest_id, prize_id])

    return (
        <Container>
            <Paper sx={{padding: 2}}>
                <Typography variant="h4" gutterBottom>
                    Contest prize
                </Typography>

                {(!prizeData || error) && <Box>
                    <Alert severity="error" sx={{marginBottom: 2}}>
                        {error ? error : "Missing prize"}
                    </Alert>
                </Box>}

                {prizeData && <Box>
                <Typography variant="h6">Contest ID</Typography>
                <Typography>{prizeData.contest_id}</Typography>
                <Typography variant="h6">Prize ID</Typography>
                <Typography>{prizeData.prize_id}</Typography>
                <Typography variant="h6">Description</Typography>
                <Typography>{prizeData.description}</Typography>
                <Typography variant="h6">Estimated value</Typography>
                <Typography>{prizeData.estimated_value}</Typography>
                <Typography variant="h6">Initial quantity</Typography>
                <Typography>{prizeData.initial_qty}</Typography>
                <Typography variant="h6">Remaining quantity</Typography>
                <Typography>{prizeData.remaining_qty}</Typography>

                {prizeData?.photo_data && <PhotoView photoData={prizeData.photo_data} />}

                {(role === "admin") && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" onClick={() => setEditOpen(true)}>
                        Edit prize
                    </Button>
                    <Button color="inherit" variant="outlined" onClick={() => deletePrize()}>
                        Delete prize
                    </Button>
                    <Button color="inherit" variant="outlined" component={Link} to={`/contests/${prizeData.contest_id}`}>
                        View contest
                    </Button>
                    <Dialog open={editOpen} onClose={() => setEditOpen(false)}>
                        <CommonEditor name="prize" fields={{"description": "text", "estimated_value": "text", "initial_qty": "text"}} defaults={{"description": prizeData.description, "estimated_value": prizeData.estimated_value, "initial_qty": prizeData.initial_qty}} callback={handleEdit} />
                    </Dialog>
                    <Button color="inherit" variant="outlined" onClick={() => setPhotoOpen(true)}>
                        Change photo
                    </Button>
                    <Dialog open={photoOpen} onClose={() => setPhotoOpen(false)}>
                        <Paper sx={{padding: 2, display: "flex", flexDirection: "column"}}>
                            {photoList && photoList.length > 0 && <form onSubmit={handlePhotoChange}>
                            <FormControl>
                                <RadioGroup value={photoChosen} onChange={(e) => setPhotoChosen(e.target.value)}>
                                    {photoList.map((value, index) => (
                                        <FormControlLabel key={index} value={index} control={<Radio />} sx={{marginBottom: 2}} label={<Paper><PhotoView photoData={value}></PhotoView></Paper>} />
                                    ))}
                                </RadioGroup>
                                <Button type="submit" variant="contained" color="primary">Change photo</Button>
                            </FormControl></form>}
                            {(!photoList || photoList.length == 0) && <Alert severity="info">No photos found</Alert>}
                        </Paper>
                    </Dialog>
                </Box>}
                {role !== "admin" && <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    <Button color="inherit" variant="outlined" component={Link} to={`/contests/${prizeData.contest_id}`}>
                        View contest
                    </Button>
                </Box>}
                </Box>}
            </Paper>
        </Container>
    )
}
