import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ILists } from "./lists.api";

@Injectable({
        providedIn: 'root'
})
export class ListsService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/lists/";

        getLists(event: bigint): Observable<ILists> {
                return this.http.get<ILists>("/"+event+this._url).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
