# django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View,
    UpdateView,
    DeleteView,
    DeleteView,
    ListView
)
from django.views.generic.edit import (
    FormView
)
# local
from applications.producto.models import Product
from applications.utils import render_to_pdf
from applications.users.mixins import VentasPermisoMixin
#
from .models import Sale, SaleDetail, CarShop
from .forms import VentaForm, VentaVoucherForm
from .functions import procesar_venta



""" 
    FORMVIEW
    Se usa para tratar dataos que no estricatmenete estan basados en un modelo 

    CREATEVIEW
    Se encarga de tratar datos, caundo los datos estan entereemnte basados ene un modelo

    VIEW
    cuando solo se necesita hacer un proceoso que inmvolucra alguno de los elementos del 
    modelo
"""

class AddCarView(VentasPermisoMixin, FormView):
    """ 
        Usamos from view para hacer procesos internos dentro de una view,
        estrictamente se sobreescribe el método form_valid
        para verificar su valides antes de mandar la infromacion
    """
    template_name = 'venta/index.html'
    form_class = VentaForm
    success_url = '.' #redirijimos a la misma pagina

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = CarShop.objects.all()
        context["total_cobrar"] = CarShop.objects.total_cobrar()
        # formulario para venta con voucher
        context['form_voucher'] = VentaVoucherForm
        return context
    
    def form_valid(self, form):
        barcode = form.cleaned_data['barcode']
        count = form.cleaned_data['count']
        obj, created = CarShop.objects.get_or_create(
            barcode=barcode,
            defaults={
                'product': Product.objects.get(barcode=barcode),
                'count': count
            }
        )
        #
        if not created:
            obj.count = obj.count + count
            obj.save()
        return super(AddCarView, self).form_valid(form)
    

""" 
    El view no neceita de un fromulario ni de ningun otro elemento
    solo, intercepta un proceso que hace un metodo post, dentro de ese post
    se indica el proceso deseado.(CRUD)
"""
class CarShopUpdateView(VentasPermisoMixin, View):
    """ quita en 1 la cantidad en un carshop """

    def post(self, request, *args, **kwargs):
        car = CarShop.objects.get(id=self.kwargs['pk'])
        if car.count > 1:
            car.count = car.count - 1
            car.save()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )

""" Elimina un elemento del carrito de compras """
class CarShopDeleteView(VentasPermisoMixin, DeleteView):
    model = CarShop # Instancia obtenida
    success_url = reverse_lazy('venta_app:venta-index')


""" Elimina todos los elementos del carrito de compraas a través de una View genérica """
class CarShopDeleteAll(VentasPermisoMixin, View):
    
    # Sobre escribe el metodo post
    def post(self, request, *args, **kwargs):
        # Para eliminar un conjunto de datos solo aplicar el delete al query realizao (all, filter.. etc)
        CarShop.objects.all().delete()
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )


class ProcesoVentaSimpleView(VentasPermisoMixin, View):
    """ Procesa una venta simple """

    def post(self, request, *args, **kwargs):
        #
        procesar_venta(
            self=self,
            type_invoce=Sale.SIN_COMPROBANTE,
            type_payment=Sale.CASH,
            user=self.request.user,
        )
        #
        return HttpResponseRedirect(
            reverse(
                'venta_app:venta-index'
            )
        )


class ProcesoVentaVoucherView(VentasPermisoMixin, FormView):
    form_class = VentaVoucherForm
    success_url = '.'
    
    def form_valid(self, form):
        type_payment = form.cleaned_data['type_payment']
        type_invoce = form.cleaned_data['type_invoce']
        #
        venta = procesar_venta(
            self=self, # se pasa el self, solo por buenas prácticas
            type_invoce=type_invoce,
            type_payment=type_payment,
            user=self.request.user,
        )
        #
        if venta: 
            return HttpResponseRedirect(
                reverse(
                    'venta_app:venta-voucher_pdf',
                    kwargs={'pk': venta.pk },
                )
            )
        else:
            return HttpResponseRedirect(
                reverse(
                    'venta_app:venta-index'
                )
            )
                


class VentaVoucherPdf(VentasPermisoMixin, View):
    
    def get(self, request, *args, **kwargs):
        venta = Sale.objects.get(id=self.kwargs['pk'])
        data = {
            'venta': venta,
            'detalle_productos': SaleDetail.objects.filter(sale__id=self.kwargs['pk'])
        }
        pdf = render_to_pdf('venta/voucher.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class SaleListView(VentasPermisoMixin, ListView):
    template_name = 'venta/ventas.html'
    context_object_name = "ventas" 

    def get_queryset(self):
        return Sale.objects.ventas_no_cerradas()



class SaleDeleteView(VentasPermisoMixin, DeleteView):
    template_name = "venta/delete.html"
    model = Sale
    success_url = reverse_lazy('venta_app:venta-index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.anulate = True
        self.object.save()
        # actualizmos sl stok y ventas
        SaleDetail.objects.restablecer_stok_num_ventas(self.object.id)
        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)

    
