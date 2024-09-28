from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image
import json
from .models import Prediction
from django.views.decorators.csrf import csrf_exempt
import cv2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Other imports remain the same

# Register view
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')
    return render(request, 'register.html')

# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')



# Load the model only once
model = None

def get_model():
    global model
    if model is None:
        model = load_model('C:/Users/Aasath/Desktop/maize/crop/c1/maize/maizemodel.h5')
    return model

def predict_disease(img_array, model):
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    return prediction

# Other imports remain the same

# Register view
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')
    return render(request, 'register.html')

# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']

        fs = FileSystemStorage()
        image_path = fs.save(image.name, image)
        image_path = fs.path(image_path)

        model = get_model()
        img = Image.open(image_path).resize((224, 224))
        img_array = img_to_array(img)
        model_prediction = predict_disease(img_array, model)

        class_names = ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy']
        predicted_class = class_names[np.argmax(model_prediction)]

        prediction_record = Prediction(image=image, disease=predicted_class, user=request.user)
        prediction_record.save()

        fs.delete(image_path)

        if predicted_class != 'Healthy':
            return redirect('solution', disease=predicted_class)
        else:
            return render(request, 'home.html', {'prediction': 'Healthy'})

    # Fetch predictions only for the logged-in user
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    
    latest_prediction = predictions.first() if predictions.exists() else None

    context = {
        'latest_prediction': latest_prediction,
        'predictions': predictions,
        'username':request.user.username,
    }
    return render(request, 'home.html',context)
  
@csrf_exempt
def webcam_predict(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            img_array = np.frombuffer(image.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224))
            img_array = img_to_array(img)

            model = get_model()
            prediction = predict_disease(img_array, model)

            class_names = ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy']
            predicted_class = class_names[np.argmax(prediction)]

            prediction_record = Prediction(disease=predicted_class)
            prediction_record.save()

            response_data = {'prediction': predicted_class}
            if predicted_class != 'Healthy':
                response_data['redirect'] = f'/solution/{predicted_class}'

            return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
def solution(request, disease):
    solutions = {
        'Blight': {
            'reason': "Blight is caused by the fungus Exserohilum turcicum, thriving in warm, humid conditions.",
            'organic': [
                "1. Neem Oil: 5-10 ml per liter of water. Antifungal properties help control blight.",
                "2. Garlic Spray: Blend 100 grams of garlic with 1 liter of water, steep overnight, strain, and spray.",
                "3. Aloe Vera Spray:Blend 100 grams of fresh Aloe Vera with 1 liter of water, strain, and use.",
                "4. Comfrey Tea: Soak 100 grams of comfrey leaves in 1 liter of water for a week, strain, and spray.",
                "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."

            ],
            'inorganic': [
                  "1. Copper Fungicides:1-2 grams per liter of water. Copper sulfate-based fungicides are effective against blight.",
                  "2. Chlorothalonil:1-1.5 grams per liter of water. A broad-spectrum fungicide.",
                  "3. Zinc Sulfate:2 grams per liter of water. Enhances plant immunity." ,
                  "4. Fosetyl-Al:1.5 grams per liter of water. Systemic fungicide that controls blight.",
                  "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."

            ]
        },
        'Common Rust': {
            'reason': "Common rust is caused by the fungus Puccinia sorghi, which thrives in cool, moist conditions.",
            'organic': [
               "1. Milk Solution: 100 ml of milk mixed with 900 ml of water. Contains proteins and fats beneficial against rust.",
               "2. Neem Oil:5-10 ml per liter of water. Antifungal properties aid in rust control.",
               "3. Onion Extract: Blend 100 grams of onions with 1 liter of water, let sit for a few hours, strain, and spray.",
               "4. Pepper Spray: Blend 50 grams of hot peppers with 1 liter of water, steep overnight, strain, and spray.",
               "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."


            ],
            'inorganic': [
                "1. Mancozeb: 2-3 grams per liter of water. Broad-spectrum fungicide.",
                "2. Propiconazole:1-1.5 ml per liter of water. Systemic fungicide effective against rust.",
                "3. Sulfur:2-3 grams per liter of water. Effective fungicide for rust control.",
                "4. Carbendazim:1 gram per liter of water. Systemic fungicide for rust and other diseases.",
                "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."

            ]
        },
        'Gray Leaf Spot': {
            'reason': "Gray leaf spot is caused by the fungus Cercospora zeae-maydis, favoring high humidity and moderate temperatures.",
            'organic': [
                "1. Baking Soda Solution:10 grams of baking soda mixed with 1 liter of water. Alters pH and inhibits fungal growth.",
                "2. Milk Spray:100 ml of milk mixed with 900 ml of water. Helps manage gray leaf spot.",
                "3. Epsom Salt Solution:10 grams of Epsom salt per liter of water. Improves plant health.",
                "4. Horsetail Tea:Steep 100 grams of horsetail plant in 1 liter of water for 24 hours, strain, and spray.",
                "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."

            ],
            'inorganic': [
                "1. Azoxystrobin:1-1.5 ml per liter of water. Systemic fungicide effective against gray leaf spot.",
                "2. Tebuconazole:1-2 ml per liter of water. Controls fungal infections including gray leaf spot.",
                "3. Mancozeb (Alternate Formulation):2-3 grams per liter of water. Effective for gray leaf spot.",
                "4. Difenoconazole:1-2 ml per liter of water. Systemic fungicide for managing gray leaf spot.",
                "These solutions should be applied according to the severity of the disease and the specific needs of the crop. Regular monitoring and appropriate timing of treatments are crucial for effective disease management."

            ]
        }
    }

    context = {
        'disease': disease,
        'reason': solutions.get(disease, {}).get('reason', ''),
        'organic_solutions': solutions.get(disease, {}).get('organic', []),
        'inorganic_solutions': solutions.get(disease, {}).get('inorganic', [])
    }

    return render(request, 'solution.html', context)



from io import BytesIO
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json

def generate_pdf(request):
    if request.method == 'POST':
        try:
            # Load data from JSON request
            data = json.loads(request.body)
            disease = data.get('disease')
            reason = data.get('reason')
            organic_solutions = data.get('organic_solutions', [])
            inorganic_solutions = data.get('inorganic_solutions', [])

            # Create buffer to hold PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()

            # Customize styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=12
            )
            heading_style = ParagraphStyle(
                'Heading2',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=12
            )
            body_style = ParagraphStyle(
                'BodyText',
                parent=styles['BodyText'],
                fontSize=12,
                spaceAfter=6
            )

            elements = []

            # Add content to the PDF
            elements.append(Paragraph(f"Disease: {disease}", title_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Reason:", heading_style))
            elements.append(Paragraph(reason, body_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Organic Solutions:", heading_style))
            for solution in organic_solutions:
                elements.append(Paragraph(f"• {solution}", body_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Inorganic Solutions:", heading_style))
            for solution in inorganic_solutions:
                elements.append(Paragraph(f"• {solution}", body_style))

            # Build PDF document
            doc.build(elements)

            # Get the PDF content from buffer
            pdf = buffer.getvalue()

            # Close the buffer
            buffer.close()

            # For debugging: Save PDF to local file to check it
            with open('output.pdf', 'wb') as f:
                f.write(pdf)

            # Prepare the HTTP response with PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="disease_solutions.pdf"'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)