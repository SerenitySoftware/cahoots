/*
 * Copyright 2011 Microsoft Corp.
 * 
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
package com.microsoft.hsg.android;

import org.xmlpull.v1.XmlPullParser;

import com.microsoft.hsg.HVException;

// TODO: Auto-generated Javadoc
/**
 * The Class Record.
 */
public class Record {
    
    /** The person id. */
    private String personId;
    
    /** The id. */
    private String id;
    
    /** The name. */
    private String name;
    
    /**
     * Instantiates a new record.
     * 
     * @param personId the person id
     * @param parser the parser
     */
    public Record(String personId, XmlPullParser parser) {
        this.personId = personId;
        try
        {
            id = parser.getAttributeValue(null, "id");
            name = parser.getAttributeValue(null, "display-name");
            XmlUtils.skipSubTree(parser);
        }
        catch(Exception e)
        {
            throw new HVException(e);
        }
    }

    /**
     * Gets the person id.
     * 
     * @return the person id
     */
    public String getPersonId() {
        return personId;
    }
    
    /**
     * Gets the id.
     * 
     * @return the id
     */
    public String getId() {
        return id;
    }
    
    /**
     * Gets the name.
     * 
     * @return the name
     */
    public String getName() {
        return name;
    }
    
    /* (non-Javadoc)
     * @see java.lang.Object#toString()
     */
    public String toString() {
        return name;
    }
}