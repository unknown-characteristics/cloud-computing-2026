export function isTokenExpired(decodedToken)
{
    if(!decodedToken.exp) return true;
    
    return decodedToken.exp < Date.now() / 1000;
}
