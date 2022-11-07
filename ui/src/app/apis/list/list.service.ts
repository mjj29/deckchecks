import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { IList } from "./list.api";

@Injectable({
        providedIn: 'root'
})
export class ListService {

        constructor(private http: HttpClient) { }

        private _url: string = "/rest/list/";

        getList(event: int, uuid: string): Observable<IPairings> {
                return this.http.get<IList>("/"+event+this._url+uuid).pipe(catchError(this.errorHandler));
        }

        errorHandler(error: HttpErrorResponse) {
                return throwError(error.message || "Server Error");
        }
}
