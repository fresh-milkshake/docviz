Package Structure
=================

This diagram shows the structure of the docviz-python package and its main components.

.. mermaid::
    :zoom:
    :caption: Repository Structure

    graph LR
    subgraph "External Dependencies"
        TT[PyMuPDF<br/>PDF Processing]
        UU[OpenCV<br/>Computer Vision]
        VV[Ultralytics<br/>Object Detection]
        WW[OpenAI<br/>LLM Integration]
        XX[Tesseract<br/>OCR Engine]
        YY[Pandas<br/>Data Analysis]
    end
    
    subgraph "docviz-python"
        subgraph "Project Configuration"
            A[pyproject.toml]
            B[README.md]
            C[LICENSE]
            D[uv.lock]
        end
        
        subgraph "Entry Points"
            direction TB
            I[CLI Interface<br/>cli/__main__.py]
            E[Package Init<br/>__init__.py]
        end
        
        subgraph "Core Infrastructure"
            direction TB
            F[constants.py]
            G[environment.py]
            H[logging.py]
        end
        
        subgraph "Type System"
            direction TB
            K[types/__init__.py]
            L[aliases.py]
            M[detection_config.py]
            N[detection_result.py]
            O[extraction_chunk.py]
            P[extraction_config.py]
            Q[extraction_result.py]
            R[extraction_type.py]
            S[llm_config.py]
            T[ocr_config.py]
            U[save_format.py]
        end
        
        subgraph "Processing Pipeline"
            direction TB
            
            subgraph "Input Layer"
                W[Document Handler<br/>document/class_.py]
                X[Document Utils<br/>document/utils.py]
            end
            
            subgraph "Detection Layer"
                Y[Detection Core<br/>detection/__init__.py]
                Z[Detection Backends<br/>backends/]
                AA[Deduplication<br/>deduplication.py]
                BB[Detection Frontend<br/>frontend.py]
                CC[Labels<br/>labels.py]
            end
            
            subgraph "Processing Layer"
                II[Image Preprocessing<br/>preprocessing.py]
                HH[Image Annotation<br/>annotate.py]
                LL[PDF Converter<br/>convert.py]
                MM[PDF Analyzer<br/>analyzer.py]
                NN[Text Extraction<br/>text_extraction.py]
            end
            
            subgraph "Extraction Layer"
                DD[Extraction Core<br/>extraction/__init__.py]
                EE[Extraction Pipeline<br/>pipeline.py]
                FF[Extraction Utils<br/>utils.py]
                JJ[Image Summarizer<br/>summarizer.py]
            end
            
            subgraph "Output Layer"
                V[Library Core<br/>lib/__init__.py]
                OO[Common Functions<br/>functions.py]
            end
        end
        
        subgraph "Resources"
            PP[Documentation<br/>docs/]
            QQ[Examples<br/>examples/]
            RR[Models<br/>models/]
            SS[Tools<br/>tools/]
        end
    end
    
    %% Entry point connections
    I --> E
    E --> F
    E --> G
    E --> H
    E --> K
    
    %% Type system connections
    K --> L
    K --> M
    K --> N
    K --> O
    K --> P
    K --> Q
    K --> R
    K --> S
    K --> T
    K --> U
    
    %% Processing flow
    W --> Y
    X --> Y
    Y --> Z
    Y --> AA
    Y --> BB
    Y --> CC
    
    Z --> II
    Z --> LL
    
    II --> HH
    II --> DD
    LL --> MM
    MM --> NN
    NN --> DD
    
    HH --> EE
    DD --> EE
    EE --> FF
    EE --> JJ
    
    FF --> V
    JJ --> V
    V --> OO
    
    %% External dependency connections
    TT -.-> W
    TT -.-> LL
    TT -.-> MM
    TT -.-> NN
    
    UU -.-> II
    UU -.-> HH
    
    VV -.-> Z
    VV -.-> Y
    
    WW -.-> JJ
    WW -.-> EE
    
    XX -.-> NN
    
    YY -.-> Q
    YY -.-> OO
    
    %% Resource connections
    PP -.-> QQ
    QQ -.-> RR
    
    %% Enhanced color scheme
    %%{init: {'theme':'dark'}}%%
    classDef config fill:#2D3748,color:#FFFFFF,stroke:#1A202C,stroke-width:2px
    classDef entry fill:#3182CE,color:#FFFFFF,stroke:#2C5AA0,stroke-width:3px
    classDef core fill:#38A169,color:#FFFFFF,stroke:#2F855A,stroke-width:2px
    classDef types fill:#805AD5,color:#FFFFFF,stroke:#6B46C1,stroke-width:2px
    classDef input fill:#E53E3E,color:#FFFFFF,stroke:#C53030,stroke-width:2px
    classDef detection fill:#0BC5EA,color:#000000,stroke:#00B5D8,stroke-width:2px
    classDef processing fill:#ED8936,color:#FFFFFF,stroke:#DD6B20,stroke-width:2px
    classDef extraction fill:#38B2AC,color:#FFFFFF,stroke:#319795,stroke-width:2px
    classDef output fill:#9F7AEA,color:#FFFFFF,stroke:#805AD5,stroke-width:2px
    classDef resources fill:#718096,color:#FFFFFF,stroke:#4A5568,stroke-width:2px
    classDef dependencies fill:#FBD38D,color:#000000,stroke:#F6AD55,stroke-width:2px
    
    class A,B,C,D config
    class I,E entry
    class F,G,H core
    class K,L,M,N,O,P,Q,R,S,T,U types
    class W,X input
    class Y,Z,AA,BB,CC detection
    class II,HH,LL,MM,NN processing
    class DD,EE,FF,JJ extraction
    class V,OO output
    class PP,QQ,RR,SS resources
    class TT,UU,VV,WW,XX,YY dependencies

Package Overview
----------------

Core Components
~~~~~~~~~~~~~~~

1. **Main Package** (``__init__.py``)
   - Exports main classes and functions
   - Handles dependency checking
   - Provides public API

2. **Types Module**
   - ``ExtractionType``: Enum for content types (TEXT, TABLE, FIGURE, EQUATION, OTHER)
   - ``SaveFormat``: Enum for output formats (JSON, CSV, EXCEL, XML)
   - ``ExtractionResult``: Main result container
   - ``ExtractionEntry``: Individual extracted content items
   - Configuration classes for detection, extraction, LLM, and OCR

3. **Library Module** (``lib/``)
   - **Document Processing**: Document class and utilities
   - **Detection**: YOLO-based layout detection
   - **Extraction**: Main extraction pipeline
   - **Image Processing**: Image analysis and chart summarization
   - **PDF Processing**: PDF conversion and text extraction

4. **CLI Module**
   - Command-line interface for document processing
   - Supports single file and batch processing
   - Rich output formatting

Key Features
~~~~~~~~~~~~

- **Document Analysis**: PDF to image conversion, layout detection
- **Content Extraction**: Text, tables, figures, equations
- **AI Integration**: Optional LLM-powered content summarization
- **Multiple Formats**: JSON, CSV, Excel, XML output
- **Batch Processing**: Handle multiple documents efficiently
- **Streaming**: Process large documents page by page
- **Async Support**: Both synchronous and asynchronous APIs

External Dependencies
~~~~~~~~~~~~~~~~~~~~~~

- **PyMuPDF**: PDF processing and conversion
- **OpenCV**: Image processing and analysis
- **Ultralytics**: YOLO model inference
- **OpenAI**: LLM integration for content summarization
- **Tesseract**: OCR for text extraction
- **Pandas**: Data manipulation and Excel export
