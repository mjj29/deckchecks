import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IPairings } from "./pairings.api";

@Injectable({
        providedIn: 'root'
})
export class PairingsService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/pairings/";

        getPairings(event: int, round: int): Observable<IPairings> {
                return this.http.get<IPairings>("/"+event+this._url+round).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
