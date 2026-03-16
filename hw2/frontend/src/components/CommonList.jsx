import { useCallback, useEffect, useState } from "react";
import { api } from "../api/api";
import { getAPIErrorMessage } from "../utils/response";
import { Alert, Box, Button, Container, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export function CommonList( {url, name = "List", id_key = "id", fields, view = true, createCallback = null} )
{
    const [error, setError] = useState();
    const [dataList, setDataList] = useState();
    
    const getList = useCallback((url) => 
    {
        api.get(url).then(response => {
            setDataList(response.data);
        }).catch(err => {
            setError(getAPIErrorMessage(err.response));
        })
    }, [])

    useEffect(() => {
        getList(url);
    }, [url, getList])

    return (
        <Container sx={{display: "flex", flexDirection: "column", gap: 2}}>
            <Paper sx = {{padding: 2}}>
                <Typography variant="h4">{name}</Typography>
                <Box sx={{display: "flex", gap: 2, marginTop: 2}}>
                    {createCallback && <Button variant="outlined" color="primary" onClick={createCallback}>Create</Button>}
                </Box>
            </Paper>
            <Paper>
                {(!dataList || error) && <Alert severity="error">{error ? error : "Couldn't get list"}</Alert>}
                {dataList && dataList.length > 0 &&
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                {fields.map(field =>
                                    <TableCell key={field}>{field}</TableCell>
                                )}
                                {view == true && <TableCell>View</TableCell>}
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {dataList.map((row, idx) => (
                                <TableRow key={idx}>
                                    {fields.map(key => 
                                        <TableCell key={key}>{row[key]}</TableCell>
                                    )}
                                    {view == true && <TableCell><Button variant="contained" color="primary" component={Link} to={`${url}/${row[id_key]}`}>View</Button></TableCell>}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>}
                {dataList && dataList.length == 0 && 
                <Alert severity="info">No entries</Alert>}
            </Paper>
        </Container>
    )
}
